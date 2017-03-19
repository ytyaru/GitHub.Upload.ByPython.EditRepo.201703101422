#!python3
#encoding:utf-8
import os
import subprocess
import shlex
import shutil
import Data
import time
import pytz
import requests
import json
import datetime

class Command:
    def __init__(self, data):
        self.data = data

    def CreateRepository(self):
        self.__CreateLocalRepository()
        r = self.__CreateRemoteRepository()
        self.__InsertRemoteRepository(r)
    def AddCommitPush(self, commit_message):
        subprocess.call(shlex.split("git add ."))
        subprocess.call(shlex.split("git commit -m '{0}'".format(commit_message)))
        subprocess.call(shlex.split("git push origin master"))
        time.sleep(3)
        self.__InsertLanguages()

    def __CreateLocalRepository(self):
        subprocess.call(shlex.split("git init"))
        subprocess.call(shlex.split("git config --local user.name '{0}'".format(self.data.get_username())))
        subprocess.call(shlex.split("git config --local user.email '{0}'".format(self.data.get_mail_address())))
        subprocess.call(shlex.split("git remote add origin git@{0}:{1}/{2}.git".format(self.data.get_ssh_host(), self.data.get_username(), self.data.get_repo_name())))

    def __CreateRemoteRepository(self):
        url = 'https://api.github.com/user/repos'
        post_data = json.dumps({"name": self.data.get_repo_name(), "description": self.data.get_repo_description(), "homepage": self.data.get_repo_homepage()})
        headers={
            "Time-Zone": "Asia/Tokyo",
            "Authorization": "token {0}".format(self.data.get_access_token(['repo']))
        }
        r = requests.post(url, data=post_data, headers=headers)
        print(r.text)
        time.sleep(3)
        return json.loads(r.text)

    def __InsertRemoteRepository(self, r):
        self.data.db_repo.begin()
        repo = self.data.db_repo['Repositories'].find_one(Name=r['name'])
        # Repositoriesテーブルに挿入する
        if None is repo:
            self.data.db_repo['Repositories'].insert(dict(
                IdOnGitHub=r['id'],
                Name=r['name'],
                Description=r['description'],
                Homepage=r['homepage'],
                CreatedAt=r['created_at'],
                PushedAt=r['pushed_at'],
                UpdatedAt=r['updated_at'],
                CheckedAt="{0:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(pytz.utc))
            ))
            repo = self.data.db_repo['Repositories'].find_one(Name=r['name'])
        # 何らかの原因でローカルDBに既存の場合はそのレコードを更新する
        else:
            self.data.db_repo['Repositories'].update(dict(
                IdOnGitHub=r['id'],
                Name=r['name'],
                Description=r['description'],
                Homepage=r['homepage'],
                CreatedAt=r['created_at'],
                PushedAt=r['pushed_at'],
                UpdatedAt=r['updated_at'],
                CheckedAt="{0:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(pytz.utc))
            ), ['Name'])

        # Countsテーブルに挿入する
        cnt = self.data.db_repo['Counts'].count(RepositoryId=repo['Id'])
        if 0 == cnt:
            self.data.db_repo['Counts'].insert(dict(
                RepositoryId=self.data.db_repo['Repositories'].find_one(Name=r['name'])['Id'],
                Forks=r['forks_count'],
                Stargazers=r['stargazers_count'],
                Watchers=r['watchers_count'],
                Issues=r['open_issues_count']
            ))
        # 何らかの原因でローカルDBに既存の場合はそのレコードを更新する
        else:
            self.data.db_repo['Counts'].update(dict(
                RepositoryId=repo['Id'],
                Forks=r['forks_count'],
                Stargazers=r['stargazers_count'],
                Watchers=r['watchers_count'],
                Issues=r['open_issues_count']
            ), ['RepositoryId'])
        self.data.db_repo.commit()

    def __InsertLanguages(self):
        url = 'https://api.github.com/repos/{0}/{1}/languages'.format(self.data.get_username(), self.data.get_repo_name())
        r = requests.get(url)
        if 300 <= r.status_code:
            print(r.status_code)
            print(r.text)
            print(url)
            raise Exception("HTTP Error {0}".format(r.status_code))
            return None
        else:
            print(r.text)

        self.data.db_repo.begin()
        repo_id = self.data.db_repo['Repositories'].find_one(Name=self.data.get_repo_name())['Id']
        self.data.db_repo['Languages'].delete(RepositoryId=repo_id)
        res = json.loads(r.text)
        for key in res.keys():
            self.data.db_repo['Languages'].insert(dict(
                RepositoryId=repo_id,
                Language=key,
                Size=res[key]
            ))
        self.data.db_repo.commit()

    def DeleteRepository(self):
        self.__DeleteLocalRepository()
        self.__DeleteRemoteRepository()
        self.__DeleteDb()
    def __DeleteLocalRepository(self):
        shutil.rmtree('.git')
    def __DeleteRemoteRepository(self):
        url = 'https://api.github.com/repos/{0}/{1}'.format(self.data.get_username(), self.data.get_repo_name())
        headers={
            "Time-Zone": "Asia/Tokyo",
            "Authorization": "token {0}".format(self.data.get_access_token(['delete_repo']))
        }
        r = requests.delete(url, headers=headers)
        if 204 != r.status_code:
            raise Exception('HTTPエラー: {0}'.format(status_code))
        time.sleep(2)
    def __DeleteDb(self):
        repo = self.data.db_repo['Repositories'].find_one(Name=self.data.get_repo_name())
        self.data.db_repo.begin()
        self.data.db_repo['Repositories'].delete(Id=repo['Id'])
        self.data.db_repo['Counts'].delete(RepositoryId=repo['Id'])
        self.data.db_repo['Languages'].delete(RepositoryId=repo['Id'])
        self.data.db_repo.commit()
    def ShowDeleteRecords(self):
        repo = self.data.db_repo['Repositories'].find_one(Name=self.data.get_repo_name())
        print(repo)
        print(self.data.db_repo['Counts'].find_one(RepositoryId=repo['Id']))
        for record in self.data.db_repo['Languages'].find(RepositoryId=repo['Id']):
            print(record)

    def EditRepository(self, name, description, homepage):
        j = self.__EditRemoteRepository(name, description, homepage)
        self.__EditDb(j)
#        self.__EditDb(name, description, homepage)
        # リポジトリ名の変更が成功したら、ディレクトリ名も変更する
        if self.data.get_repo_name() != name:
            os.rename("../" + self.data.get_repo_name(), "../" + name)
    def __EditRemoteRepository(self, name, description, homepage):
        # リポジトリ名は必須
        url = 'https://api.github.com/repos/{0}/{1}'.format(self.data.get_username(), self.data.get_repo_name())
        headers={
            "Time-Zone": "Asia/Tokyo",
            "Authorization": "token {0}".format(self.data.get_access_token())
        }
        data = {}
        data['name'] = name
        if not(None is description or '' == description):
            data['description'] = description
        if not(None is homepage or '' == homepage):
            data['homepage'] = homepage
        r = requests.patch(url, headers=headers, data=json.dumps(data))
        if 200 != r.status_code:
            raise Exception('HTTPエラー: {0}'.format(r.status_code))
        time.sleep(2)
        return json.loads(r.text)
#    def __EditDb(self, name, description, homepage):
    def __EditDb(self, j):
        repo = self.data.db_repo['Repositories'].find_one(Name=self.data.get_repo_name())
        """
        data = {}
        data['Id'] = repo['Id']
        data['Name'] = name
        if not(None is description or '' == description):
            data['Description'] = description
        if not(None is homepage or '' == homepage):
            data['Homepage'] = homepage
        """
        data = {}
        data['Id'] = repo['Id']
        data['Name'] = j['name']
        if not(None is j['description'] or '' == j['description']):
            data['Description'] = j['description']
        if not(None is j['homepage'] or '' == j['homepage']):
            data['Homepage'] = j['homepage']
        data['CreatedAt']=j['created_at']
        data['PushedAt']=j['pushed_at']
        data['UpdatedAt']=j['updated_at']
        data['CheckedAt']="{0:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(pytz.utc))
        self.data.db_repo['Repositories'].update(data, ['Id'])
