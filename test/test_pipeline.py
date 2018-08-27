import unittest
import pdal
import os
import numpy as np

DATADIRECTORY = "./test/data"

bad_json = u"""
{
  "pipeline": [
    "nofile.las",
    {
        "type": "filters.sort",
        "dimension": "X"
    }
  ]
}
"""



class PDALTest(unittest.TestCase):

    def fetch_json(self, filename):
        import os
        fn = DATADIRECTORY + os.path.sep +  filename
        output = ''
        with open(fn, 'rb') as f:
            output = f.read().decode('UTF-8')
        return output

class TestPipeline(PDALTest):
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'sort.json')),
                         "missing test data")
    def test_construction(self):
        """Can we construct a PDAL pipeline"""
        json = self.fetch_json('sort.json')
        r = pdal.Pipeline(json)
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'sort.json')),
                         "missing test data")
    def test_execution(self):
        """Can we execute a PDAL pipeline"""
        x = self.fetch_json('sort.json')
        r = pdal.Pipeline(x)
        r.validate()
        r.execute()
        self.assertGreater(len(r.pipeline), 200)
#
    def test_validate(self):
        """Do we complain with bad pipelines"""
        r = pdal.Pipeline(bad_json)
        with self.assertRaises(RuntimeError):
            r.validate()
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'sort.json')),
                         "missing test data")
    def test_array(self):
        """Can we fetch PDAL data as a numpy array"""
        json = self.fetch_json('sort.json')
        r = pdal.Pipeline(json)
        r.validate()
        r.execute()
        arrays = r.arrays
        self.assertEqual(len(arrays), 1)
#
        a = arrays[0]
        self.assertAlmostEqual(a[0][0], 635619.85, 7)
        self.assertAlmostEqual(a[1064][2], 456.92, 7)
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'sort.json')),
                         "missing test data")
    def test_metadata(self):
        """Can we fetch PDAL metadata"""
        json = self.fetch_json('sort.json')
        r = pdal.Pipeline(json)
        r.validate()
        r.execute()
        metadata = r.metadata
        import json
        j = json.loads(metadata)
        self.assertEqual(j["metadata"]["readers.las"][0]["count"], 1065)
#
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'sort.json')),
                         "missing test data")
    def test_no_execute(self):
        """Does fetching arrays without executing throw an exception"""
        json = self.fetch_json('sort.json')
        r = pdal.Pipeline(json)
        with self.assertRaises(RuntimeError):
            r.arrays
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'reproject.json')),
                         "missing test data")
    def test_logging(self):
        """Can we fetch log output"""
        json = self.fetch_json('reproject.json')
        r = pdal.Pipeline(json)
        r.loglevel = 8
        r.validate()
        count = r.execute()
        self.assertEqual(count, 789)
        self.assertEqual(r.log.split()[0], '(pypipeline')
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'sort.json')),
                         "missing test data")
    def test_schema(self):
        """Fetching a schema works"""
        json = self.fetch_json('sort.json')
        r = pdal.Pipeline(json)
        r.validate()
        r.execute()
        self.assertEqual(r.schema['schema']['dimensions'][0]['name'], 'X')
#
    @unittest.skipUnless(os.path.exists(os.path.join(DATADIRECTORY, 'chip.json')),
                         "missing test data")
    def test_merged_arrays(self):
        """Can we fetch multiple point views from merged PDAL data """
        json = self.fetch_json('chip.json')
        r = pdal.Pipeline(json)
        r.validate()
        r.execute()
        arrays = r.arrays
        self.assertEqual(len(arrays), 43)
#
class TestArrayLoad(PDALTest):

    def test_merged_arrays(self):
        """Can we load data from a a list of arrays to PDAL"""
        data = np.load(os.path.join(DATADIRECTORY, 'perlin.npy'))

        arrays = [data, data, data]
        arrays = [data]

        json = self.fetch_json('chip.json')
        chip ="""{
  "pipeline":[
    {
      "type":"filters.range",
      "limits":"Intensity[0:0.10]"
    }
  ]
}"""

        p = pdal.Pipeline(chip, arrays)
        p.loglevel = 8
        count = p.execute()
        arrays = p.arrays
        self.assertEqual(len(arrays), 1)

        data = arrays[0]
        self.assertEqual(len(data), 1836)

class TestDimensions(PDALTest):
    def test_fetch_dimensions(self):
        """Ask PDAL for its valid dimensions list"""
        dims = pdal.dimensions
        self.assertEqual(len(dims), 72)

def test_suite():
    return unittest.TestSuite(
        [TestPipeline])

if __name__ == '__main__':
    unittest.main()
