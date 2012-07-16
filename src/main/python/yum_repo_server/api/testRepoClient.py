import httplib

from yum_repo_client.repoclient import RepoException
from yum_repo_server.test.testconstants import Constants
from yum_repo_server.test.baseIntegrationTestCase import BaseIntegrationTestCase
from yum_repo_client.repoclient import CommandLineClient

class TestRepoClient(BaseIntegrationTestCase):
    
    def test_create_repo(self):
        reponame = self.uniqueRepoName();
        self._execute(['create', reponame]);
        response = self.doHttpGet('/repo/' + reponame + '/')
        self.assertStatusCode(response, httplib.OK)
        
    def test_upload_rpm(self):
        reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self._execute(['uploadto', reponame, testRPMFilePath])
        response = self.doHttpGet('/repo/' + reponame + '/' + Constants.TEST_RPM_DESTINATION_NAME)
        self.assertStatusCode(response, httplib.OK)
        
    def test_delete_rpm(self):
        reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(reponame, testRPMFilePath)
        self._execute(['deleterpm', reponame, Constants.TEST_RPM_DESTINATION_NAME]);
        response = self.doHttpGet('/repo/' + reponame + '/' + Constants.TEST_RPM_DESTINATION_NAME)
        self.assertStatusCode(response, httplib.NOT_FOUND)
        
    def test_generatemetadata(self):
        reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(reponame, testRPMFilePath)
        self._execute(['generatemetadata', reponame]);
        response = self.doHttpGet('/repo/' + reponame + '/repodata/repomd.xml')
        self.assertStatusCode(response, httplib.OK)
        
    def test_linktostatic(self):
        static_reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(static_reponame, testRPMFilePath)
        virtual_reponame = self.uniqueRepoName()
        self._execute(['linktostatic', virtual_reponame, static_reponame])
        response = self.doHttpGet('/repo/virtual/' + virtual_reponame + '/' + Constants.TEST_RPM_DESTINATION_NAME)
        self.assertStatusCode(response, httplib.OK)
        
    def test_linktovirtual(self):
        static_reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(static_reponame, testRPMFilePath)
        virtual_reponame = self.uniqueRepoName()
        self.create_virtual_repo_from_static_repo(virtual_reponame, static_reponame)
        virtual_reponame2 = self.uniqueRepoName()
        self._execute(['linktovirtual', virtual_reponame2, virtual_reponame])
        response = self.doHttpGet('/repo/virtual/' + virtual_reponame2 + '/' + Constants.TEST_RPM_DESTINATION_NAME)
        self.assertStatusCode(response, httplib.OK)
        
    def test_deletevirtual(self):
        static_reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(static_reponame, testRPMFilePath)
        virtual_reponame = self.uniqueRepoName()
        self.create_virtual_repo_from_static_repo(virtual_reponame, static_reponame)
        self._execute(['deletevirtual', virtual_reponame])
        response = self.doHttpGet('/repo/virtual/' + virtual_reponame + '/')
        self.assertStatusCode(response, httplib.NOT_FOUND)
        
    def test_upload_of_invalid_rpm(self):
        reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_CORRUPT_RPM
        self.assertEquals(1, self._execute(['uploadto', reponame, testRPMFilePath]))    
    
    def _execute(self, arguments):
        return CommandLineClient(self._baseargs() + arguments).execute()
        
    def _baseargs(self):
        return ['', '--hostname=' + self.live_server_host, '--port=' + self.live_server_port.__str__()]