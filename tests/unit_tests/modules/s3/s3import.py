# -*- coding: utf-8 -*-
#
# S3 XML Importer Unit Tests
#
# To run this script use:
# python web2py.py -S eden -M -R applications/eden/tests/unit_tests/modules/s3/s3import.py
#
import unittest

# =============================================================================
class S3ComponentDisambiguationTests(unittest.TestCase):
    """ Test component disambiguation using the alias-attribute """

    def setUp(self):

        xmlstr1 = """
<s3xml>
    <resource name="org_organisation">
        <data field="name">MasterOrg1</data>
        <resource name="org_organisation_branch" alias="branch">
            <reference field="branch_id" tuid="TUID_OF_THE_BRANCH_ORG"/>
        </resource>
    </resource>
    <resource name="org_organisation" tuid="TUID_OF_THE_BRANCH_ORG">
        <data field="name">BranchOrg1</data>
    </resource>
</s3xml>"""

        xmlstr2 = """
<s3xml>
    <resource name="org_organisation">
        <data field="name">BranchOrg2</data>
            <resource name="org_organisation_branch" alias="parent">
                <reference field="organisation_id" tuid="TUID_OF_THE_MASTER_ORG"/>
            </resource>
    </resource>
    <resource name="org_organisation" tuid="TUID_OF_THE_MASTER_ORG">
        <data field="name">MasterOrg2</data>
    </resource>
</s3xml>"""

        from lxml import etree
        self.branch_tree = etree.ElementTree(etree.fromstring(xmlstr1))
        self.parent_tree = etree.ElementTree(etree.fromstring(xmlstr2))

    def testOrganisationBranchImport(self):
        """ Test import of organisation branches using alias-attribute """

        auth.override = True
        resource = s3mgr.define_resource("org", "organisation")
        msg = resource.import_xml(self.branch_tree)

        table = resource.table

        query = (table.name == "MasterOrg1")
        master = db(query).select(table._id, limitby=(0, 1)).first()
        self.assertNotEqual(master, None)

        query = (table.name == "BranchOrg1")
        branch = db(query).select(table._id, limitby=(0, 1)).first()
        self.assertNotEqual(branch, None)

        table = s3db.org_organisation_branch
        query = (table.organisation_id == master.id) & \
                (table.branch_id == branch.id)
        link = db(query).select(limitby=(0, 1)).first()
        self.assertNotEqual(link, None)

    def testParentImport(self):
        """ Test import of organisation parents using alias-attribute """

        auth.override = True
        resource = s3mgr.define_resource("org", "organisation")
        msg = resource.import_xml(self.parent_tree)

        table = resource.table

        query = (table.name == "MasterOrg2")
        master = db(query).select(table._id, limitby=(0, 1)).first()
        self.assertNotEqual(master, None)

        query = (table.name == "BranchOrg2")
        branch = db(query).select(table._id, limitby=(0, 1)).first()
        self.assertNotEqual(branch, None)

        table = s3db.org_organisation_branch
        query = (table.organisation_id == master.id) & \
                (table.branch_id == branch.id)
        link = db(query).select(limitby=(0, 1)).first()
        self.assertNotEqual(link, None)

    def tearDown(self):

        db.rollback()

# =============================================================================
def run_suite(*test_classes):
    """ Run the test suite """

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    if suite is not None:
        unittest.TextTestRunner(verbosity=2).run(suite)
    return

if __name__ == "__main__":

    run_suite(
        S3ComponentDisambiguationTests,
    )

# END ========================================================================
