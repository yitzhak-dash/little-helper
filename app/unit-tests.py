import unittest
from app.artifactory_frog_api import ArtifactsFrog, get_latest_build


class TestsFrogApi(unittest.TestCase):
    def test_get_latest_build(self):
        builds = [
            'http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/127/',
            'http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/137/',
            'http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/150/',
            'http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/111/',
            'http://ccs-artifact-01.c4internal.c4-security.com:8081/artifactory/apd/CI/web-gui/130/',
        ]
        frog = ArtifactsFrog()
        self.assertEqual(get_latest_build(builds).split('/')[-2], '150')

    def test_download_build_num_150(self):
        self.assertEquals(False, True)


if __name__ == '__main__':
    unittest.main()
