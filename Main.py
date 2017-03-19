#!python3
#encoding:utf-8
import os.path
import subprocess
import Data
import Command
import Aggregate

class Main:
    def __init__(self, user_name, description, homepage, path_dir_pj, path_db_account, path_db_repo):
        self.data = Data.Data(user_name, description, homepage, path_dir_pj, path_db_account, path_db_repo)
        self.user_name = user_name
        self.description = description
        self.homepage = homepage
        self.path_dir_pj = path_dir_pj
        self.cmd = Command.Command(self.data)
        self.agg = Aggregate.Aggregate(self.data)

    def Run(self):
        if -1 != self.__Create():
            self.__Commit()

    def __CreateInfo(self):
        print('ユーザ名: ' + self.data.get_username())
        print('メアド: ' + self.data.get_mail_address())
        print('SSH HOST: ' + self.data.get_ssh_host())
        print('リポジトリ名: ' + self.data.get_repo_name())
        print('説明: ' + self.data.get_repo_description())
        print('URL: ' + self.data.get_repo_homepage())
        print('リポジトリ情報は上記のとおりで間違いありませんか？[y/n]')

    def __Create(self):
        if os.path.exists(".git"):
            return 0
        answer = ''
        while '' == answer:
            self.__CreateInfo()
            answer = input()
            if 'y' == answer or 'Y' == answer:
                self.cmd.CreateRepository()
                return 0
            elif 'n' == answer or 'N' == answer:
                print('conf.iniを編集して再度やり直してください。')
                return -1
            else:
                answer = ''

    def __CommitInfo(self):
        print('リポジトリ名： {0}/{1}'.format(self.data.get_username(), self.data.get_repo_name()))
        print('説明: ' + self.data.get_repo_description())
        print('URL: ' + self.data.get_repo_homepage())
        print('----------------------------------------')
        subprocess.call('git add -n .'.split(" "))
        print('commit,pushするならメッセージを入力してください。Enterかnで終了します。')
        print('サブコマンド    n:終了 a:集計 e:編集 d:削除 i:Issue作成')

    def __Commit(self):
        self.__CommitInfo()
        answer = input()
        if '' == answer or 'n' == answer or 'N' == answer:
            print('何もせず終了します。')
        elif 'a' == answer or 'A' == answer:
            self.agg.Show()
        elif 'e' == answer or 'E' == answer:
            self.__ConfirmEdit()
        elif 'd' == answer or 'D' == answer:
            self.__ConfirmDelete()
        elif 'i' == answer or 'I' == answer:
            print('(Issue作成する。(未実装))')
        else:
            self.cmd.AddCommitPush(answer)
            self.agg.Show()

    def __ConfirmDelete(self):
        print('.gitディレクトリ、対象リモートリポジトリ、対象DBレコードを削除します。')
        print('リポジトリ名： {0}/{1}'.format(self.data.get_username(), self.data.get_repo_name()))
        self.cmd.ShowDeleteRecords()
        print('削除すると復元できません。本当に削除してよろしいですか？[y/n]')
        answer = input()
        if 'y' == answer or 'Y' == answer:
            self.cmd.DeleteRepository()
            print('削除しました。')
            return True
        else:
            print('削除を中止しました。')
            self.__Commit()
            return False

    def __ConfirmEdit(self):
        print('変更したくない項目は無記入のままEnterキー押下してください。')
        print('リポジトリ名を入力してください。')
        name = input()
        if None is name or '' == name:
            # 名前は必須項目。変更しないなら現在の名前をセットする
            name = self.data.get_repo_name()
        print('説明文を入力してください。')
        description = input()
        print('Homepageを入力してください。')
        homepage = input()
        # 変更がないなら編集しない
        if '' == description and '' == homepage and self.data.get_repo_name() == name:
            print('編集せず終了します。')
        else:
            self.cmd.EditRepository(name, description, homepage)
            print('編集しました。')
            """
            print('名前: ' + name)
            print('説明: ' + description)
            print('URL: ' + homepage)
            print('上記のように編集します。よろしいですか？[y/n]')
            answer = input()
            if 'y' == answer or 'Y' == answer:
                self.cmd.EditRepository(name, description, homepage)
                print('編集しました。')
            else:
                print('編集せず終了します。')
            """
