import logging
import numpy as np
import unittest

from pyspark.sql import SparkSession
from zarr_spark import repartition_chunks


class TestZarrSpark(unittest.TestCase):

    # based on https://blog.cambridgespark.com/unit-testing-with-pyspark-fb31671b1ad8
    @classmethod
    def suppress_py4j_logging(cls):
        logger = logging.getLogger('py4j')
        logger.setLevel(logging.WARN)

    @classmethod
    def create_testing_pyspark_session(cls):
        return (SparkSession.builder
                .master('local[2]')
                .appName('my-local-testing-pyspark-context')
                .getOrCreate())

    @classmethod
    def setUpClass(cls):
        cls.suppress_py4j_logging()
        cls.spark = cls.create_testing_pyspark_session()
        cls.sc = cls.spark.sparkContext

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_repartition_chunks_no_op(self):
        old_rows = [
            np.array([[1.], [2.], [3.]]),
            np.array([[4.], [5.], [6.]]),
            np.array([[7.], [8.]])
        ]
        old_rows_rdd = self.sc.parallelize(old_rows, len(old_rows))
        new_rows_rdd = repartition_chunks(self.sc, old_rows_rdd, (3, 1))
        new_rows = new_rows_rdd.collect()
        for i in range(len(old_rows)):
            self.assertTrue(np.array_equal(new_rows[i], old_rows[i]))

    def test_repartition_chunks_uneven(self):
        old_rows = [
            np.array([[1.], [2.], [3.], [4.]]),
            np.array([[5.], [6.], [7.]]),
            np.array([[8.], [9.], [10.], [11.]])
        ]
        old_rows_rdd = self.sc.parallelize(old_rows, len(old_rows))
        new_rows_rdd = repartition_chunks(self.sc, old_rows_rdd, (3, 1))
        new_rows = new_rows_rdd.collect()
        new_rows_expected = [
            np.array([[1.], [2.], [3.]]),
            np.array([[4.], [5.], [6.]]),
            np.array([[7.], [8.], [9.]]),
            np.array([[10.], [11.]])
        ]
        for i in range(len(new_rows_expected)):
            self.assertTrue(np.array_equal(new_rows[i], new_rows_expected[i]))

    def test_repartition_chunks_subdivide(self):
        old_rows = [
            np.array([[1.], [2.], [3.], [4.]]),
            np.array([[5.], [6.], [7.], [8.]])
        ]
        old_rows_rdd = self.sc.parallelize(old_rows, len(old_rows))
        new_rows_rdd = repartition_chunks(self.sc, old_rows_rdd, (2, 1))
        new_rows = new_rows_rdd.collect()
        new_rows_expected = [
            np.array([[1.], [2.]]),
            np.array([[3.], [4.]]),
            np.array([[5.], [6.]]),
            np.array([[7.], [8.]])
        ]
        for i in range(len(new_rows_expected)):
            self.assertTrue(np.array_equal(new_rows[i], new_rows_expected[i]))

    def test_repartition_chunks_coalesce(self):
        old_rows = [
            np.array([[1.], [2.]]),
            np.array([[3.], [4.]]),
            np.array([[5.], [6.]]),
            np.array([[7.], [8.]])
        ]
        old_rows_rdd = self.sc.parallelize(old_rows, len(old_rows))
        new_rows_rdd = repartition_chunks(self.sc, old_rows_rdd, (4, 1))
        new_rows = new_rows_rdd.collect()
        new_rows_expected = [
            np.array([[1.], [2.], [3.], [4.]]),
            np.array([[5.], [6.], [7.], [8.]])
        ]
        for i in range(len(new_rows_expected)):
            self.assertTrue(np.array_equal(new_rows[i], new_rows_expected[i]))

if __name__ == '__main__':
    unittest.main()