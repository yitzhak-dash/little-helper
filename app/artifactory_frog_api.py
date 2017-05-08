import sys
from artifactory import ArtifactoryPath
import ntpath
import threading
import os


def get_latest_build(builds):
    """
    find latest build
    :return:
    """
    if len(builds) == 0:
        return None
    return sorted(builds)[-1]


class ArtifactsFrog:
    # repoPath = "http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/{build_num}/Installers"
    # repoPath = "http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/150/Installers"
    repoPath = 'http://repo.jfrog.org/artifactory/distributions/org/apache/tomcat/'

    def __init__(self, user=None, password=None):
        self.artifactory_repo = None
        self.auth = True
        self.user = user
        self.password = password
        if user is None or password is None:
            self.auth = False
        self.__init_artifactory_repo()

    def __init_artifactory_repo(self):
        # if created yet, then return it
        if self.artifactory_repo is not None:
            return self.artifactory_repo
        self.artifactory_repo = self.__create_artifactory_path(ArtifactsFrog.repoPath)
        return self.artifactory_repo

    def __create_artifactory_path(self, path):
        if self.auth:
            res = ArtifactoryPath(ArtifactsFrog.repoPath, auth=(self.user, self.password))
        else:
            res = ArtifactoryPath(ArtifactsFrog.repoPath)
            res.touch()
        return res

    def get_repo_content(self):
        res = []
        for p in self.artifactory_repo:
            res.append(p)
        return res

    def download_build(self, build_name=None, target_dir='build', print_callback=None):
        """
        find build name and download all files
        if build number is none then download latest build
        :param build_num:
        :return:
        """
        postfix = 'Installers'
        if build_name is None:
            build_path = get_latest_build(self.get_repo_content())
        else:
            build_path = ntpath.join(self.artifactory_repo, build_name)
        # start download
        artifactory_path = self.__create_artifactory_path(ntpath.join(build_path, postfix))
        threads = []
        for p in artifactory_path:
            thread = threading.Thread(target=self.download, args=(p, target_dir, print_callback,))
            threads.append(thread)

        # start all threads
        for thread in threads:
            thread.start()
        # wait for all of them to finish
        for thread in threads:
            thread.join()
        return True

    def download(self, path, target_dir, print_callback=None):
        with path.open() as fd:
            with open(os.path.join(target_dir, ntpath.basename(path)), 'wb') as out:
                out.write(fd.read())
                if print_callback is not None:
                    print_callback('file: {1}\tdownloaded to: {0}'.format(target_dir, ntpath.basename(path)))


if __name__ == '__main__':
    user = None
    password = None

    if len(sys.argv) == 3:
        user = sys.argv[1]
        password = sys.argv[2]

    frog = ArtifactsFrog(user=user, password=password)
    print(frog.get_repo_content())
