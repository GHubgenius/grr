#!/usr/bin/env python
# -*- mode: python; encoding: utf-8 -*-

# Copyright 2010 Google Inc. All Rights Reserved.
"""Test client vfs."""

import hashlib
import os


from grr_response_client.client_actions import file_fingerprint
from grr.lib import flags
from grr.lib.rdfvalues import client as rdf_client
from grr.lib.rdfvalues import paths as rdf_paths
from grr.test_lib import client_test_lib
from grr.test_lib import test_lib


class FilehashTest(client_test_lib.EmptyActionTest):
  """Test fingerprinting files."""

  def testHashFile(self):
    """Can we hash a file?"""
    path = os.path.join(self.base_path, "numbers.txt")
    p = rdf_paths.PathSpec(path=path, pathtype=rdf_paths.PathSpec.PathType.OS)
    result = self.RunAction(
        file_fingerprint.FingerprintFile,
        rdf_client.FingerprintRequest(pathspec=p))
    types = result[0].matching_types
    fingers = {}
    for f in result[0].results:
      fingers[f["name"]] = f
    generic_sha256 = fingers["generic"]["sha256"]
    self.assertEqual(generic_sha256,
                     hashlib.sha256(open(path, "rb").read()).digest())

    # Make sure all fingers are listed in types and vice versa.
    t_map = {
        rdf_client.FingerprintTuple.Type.FPT_GENERIC: "generic",
        rdf_client.FingerprintTuple.Type.FPT_PE_COFF: "pecoff"
    }
    ti_map = dict((v, k) for k, v in t_map.iteritems())
    for t in types:
      self.assertTrue(t_map[t] in fingers)
    for f in fingers:
      self.assertTrue(ti_map[f] in types)

    self.assertEqual(result[0].pathspec.path, path)

  def testMissingFile(self):
    """Fail on missing file?"""
    path = os.path.join(self.base_path, "this file does not exist")
    p = rdf_paths.PathSpec(path=path, pathtype=rdf_paths.PathSpec.PathType.OS)
    self.assertRaises(
        IOError,
        self.RunAction,
        file_fingerprint.FingerprintFile,
        rdf_client.FingerprintRequest(pathspec=p))


def main(argv):
  test_lib.main(argv)


if __name__ == "__main__":
  flags.StartMain(main)
