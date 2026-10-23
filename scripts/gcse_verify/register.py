"""Verification register: which GCSE maths slots are verified, pending, or pinned.

The register is the ratchet.  Every topic is in VERIFIED_TOPICS and verified slot by slot; a new topic must be
added there with its solvers (PENDING_TOPICS is empty and the test fails if anything is left pending).  Static MCQ bank items
are reviewed by a person and pinned by digest; changing or adding an item fails the test until the item
is re-reviewed and its digest updated (run the test with --print-digests).
"""
from __future__ import annotations

VERIFIED_TOPICS = (
    'number', 'ratio_proportion', 'bidmas', 'multiples_factors', 'decimals', 'fdp',
    'pythagoras', 'compound_measures', 'mensuration', 'trigonometry', 'bearings',
    # Phase 2 (algebra)
    'algebra', 'equations_inequalities', 'changing_the_subject', 'sequences', 'surds',
    'simultaneous_equations', 'completing_the_square', 'quadratic_simultaneous_equations', 'graphs',
    'graphical_simultaneous_equations', 'algebraic_fractions', 'functions', 'algebraic_proof',
    # Phase 3
    'statistics', 'probability', 'geometry_angles', 'transformations',
    'similarity_congruence', 'circle_theorems', 'constructions_loci', 'vectors',
)

# The Phase 2 (algebra) topics: heavier solvers, so the default run uses fewer seeds for them.
ALGEBRA_TOPICS = (
    'algebra', 'equations_inequalities', 'changing_the_subject', 'sequences', 'surds',
    'simultaneous_equations', 'completing_the_square', 'quadratic_simultaneous_equations', 'graphs',
    'graphical_simultaneous_equations', 'algebraic_fractions', 'functions', 'algebraic_proof',
)

# The Phase 3 topics (statistics, probability, geometry): their questions get the same cosmetic algebra check.
PHASE3_TOPICS = (
    'statistics', 'probability', 'geometry_angles', 'transformations',
    'similarity_congruence', 'circle_theorems', 'constructions_loci', 'vectors',
)

PENDING_TOPICS = ()

# Slots in verified topics that cannot be re-solved, with the reason.  Key: 'slug/mode/fn'.  Empty in Phase 1.
EXEMPT = {
    'similarity_congruence/standard/_sc_i9_proof_aa_parallel': (
        'infeasible', 'Worded proof (similar triangles by AA) answered by ordering sentences; there is no numeric '
        'or symbolic form to recompute. The keyed order and the four wrong steps were read by hand.'),
    'similarity_congruence/standard/_sc_d1_midpoint_theorem_proof': (
        'infeasible', 'Worded proof of the midpoint theorem answered by ordering sentences; nothing to recompute. '
        'The keyed order and the wrong steps were read by hand.'),
    'circle_theorems/standard/_ct_d2_prove_angle': (
        'infeasible', 'Worded proof of the angle at the centre theorem answered by ordering sentences; nothing to '
        'recompute. The keyed order and the five wrong steps were read by hand.'),
    'circle_theorems/standard/_ct_d4_alternate_segment_proof': (
        'infeasible', 'Worded proof of the alternate segment theorem answered by ordering sentences; nothing to '
        'recompute. The keyed order and the five wrong steps were read by hand.'),
    'circle_theorems/standard/_ct_d10_prove_cyclic': (
        'infeasible', 'Worded proof of the converse of the cyclic quadrilateral theorem answered by ordering '
        'sentences; nothing to recompute. The keyed order and the wrong steps were read by hand.'),
    'constructions_loci/standard/_cl_d1_locus_proof': (
        'infeasible', 'Fixed-stem worded proof (the locus of points equidistant from two points) answered by '
        'ordering sentences; nothing to recompute. The keyed order and the five wrong steps were read by hand.'),
    'similarity_congruence/standard/_sc_d7_congruence_proof': (
        'infeasible', 'Worded congruence proof answered by ordering sentences; nothing to recompute. '
        'Both proofs (isosceles and parallelogram) and their wrong steps were read by hand.'),
}

# Ordered-proof slots whose steps are not a strict chain: the pairs of canonical step positions (1-based) that a
# person read and judged logically independent, so a pupil may put them either way round (decided 2026-10-23,
# docs/GCSE_MATHS_VERIFICATION.md "Decisions").  The test compares this with the order spec each problem carries;
# an ordered-proof slot that is not listed here must be a strict chain, so adding or widening an alternative order
# in a generator fails the test until the pairs are re-read and listed.  Key: 'slug/mode/fn'.
ORDER_FREE_PAIRS = {
    'algebraic_proof/standard/_ap_f_even_form': frozenset({(1, 2), (1, 3)}),
    'algebraic_proof/standard/_ap_f_odd_form': frozenset({(1, 2)}),
    'algebraic_proof/standard/_ap_i_product_consecutive': frozenset({(3, 4)}),
    'algebraic_proof/standard/_ap_d_n_squared_plus_n': frozenset({(3, 4)}),
    'similarity_congruence/standard/_sc_i9_proof_aa_parallel': frozenset({(1, 3), (2, 3)}),
    'similarity_congruence/standard/_sc_d1_midpoint_theorem_proof': frozenset({(1, 3), (2, 3), (5, 6)}),
    'similarity_congruence/standard/_sc_d7_congruence_proof': frozenset({(1, 2), (1, 3), (2, 3)}),
    'circle_theorems/standard/_ct_d2_prove_angle': frozenset({(2, 3)}),
    'circle_theorems/standard/_ct_d10_prove_cyclic': frozenset({(1, 2), (1, 3), (2, 3)}),
    'constructions_loci/standard/_cl_i2_equilateral_triangle': frozenset({(1, 2)}),
    'constructions_loci/standard/_cl_i11_circumcircle': frozenset({(1, 2)}),
    'constructions_loci/standard/_cl_i12_incircle': frozenset({(1, 2)}),
    'constructions_loci/standard/_cl_d1_locus_proof': frozenset(
        {(1, 5), (1, 6), (2, 5), (2, 6), (2, 7), (3, 5), (3, 6), (3, 7), (4, 5), (4, 6), (4, 7)}),
    'sequences/standard/_seq_diff_show_divisible': frozenset({(1, 2)}),
    'sequences/standard/_seq_diff_arithmetic_proof': frozenset({(1, 2)}),
    'vectors/standard/_vectors_diff_vector_inequality': frozenset({(1, 2)}),
}

# Reviewed static MCQ bank items: topic -> digests (see mcq.item_digest).  Digests are over the question,
# the sorted option texts and the keyed text, so shuffling options or editing the solution text is allowed.
STATIC_ITEMS = {
    'bidmas': frozenset({
        '000b2f7bf5fa', '090102e52a4c', '198ad44fd5c0', '1e2b1883daf4', '46a8c827b617',
        '4bc29cddfee2', '6175fde23c7a', '7179d4c76daf', '734d9ce38036', '8d4d452d5137',
        'aeb202fa4816', 'c34249ff6ac5', 'cd341dacece6', 'd2ad3f201b3c', 'de6a72371a71',
    }),
    'fdp': frozenset({
        '0510547f2998', '27f3a73ae928', '3757907ddc80', '38aeab7adb0f', '3cd0c1ef24c4',
        '531a98af4ca9', '55baec307617', '5b146eae23a1', '5c46977a9f20', '63ff7ac08d0a',
        '7373f1c0ff22', '7ab26dbec5b5', '928c205e3716', 'a0910ef9d500', 'b2de8d6815d0',
        'b75710af999f', 'c517a599698e', 'c9cad793dd4b', 'ca4bed529ea7', 'cffd533ea26c',
        'd85b97b3c4a0', 'd9eccb616a3d', 'dd97af4c33f0', 'e4ae98ad32ff', 'f19eb05d36ac',
    }),
    'multiples_factors': frozenset({
        '11433e9d06aa', '1c0e4946c132', '2372f0de4ba1', '2b98ac3d2294', '32cbbc6e84a6',
        '3f415f0e59a4', '41857bb1029e', '4275d70a92b9', '46b407f316cd', '650b4ae17fba',
        '762d08cec45b', '76cf4d6edee6', '77cc5fa750c5', '8c62f0da7244', '9341b5963474',
        '9cb2528b5cda', '9fc10ebbcc29', 'ba8030a7d2f7', 'bbe085a5eb2e', 'c2e4dbb0ce39',
        'ca4d350cfb9e', 'cbd06ecb1dad', 'e658a77a98eb', 'e7494c37dc0f', 'e7a10ff5f23b',
    }),
    'decimals': frozenset({
        '0480831ed0a9', '0bad6320cd7c', '0d3627d1f62c', '460a2f5b9ee9', '4e23096ddb5c',
        '6c57f67cad4a', '6e3177c902a1', '6fbbd1012207', '70662c177240', '773812c6456e',
        '8e00daa8ae72', '9fcb67f84d9d', 'bc57517553bf', 'c4a44cd8e194', 'cf371e9e4594',
        'd1697344d644', 'f0f652072911', 'fbab5153e41b',
    }),
    'pythagoras': frozenset({
        '230298cd2634', '46d54d281364', '6ecb3b0c8247', '75d34ba89aa3', '81906023f08c',
        '8887750e9f47', '9268cccf7426', 'bbd4b325472c', 'e034b9e8ec2f', 'ea9c92542c88',
    }),
    'compound_measures': frozenset({
        '08144339f331', '132df6323edf', '19bfcfc74bce', '1f7872830aba', '2e2a48c231b3',
        '30c7e55e1e43', '61e088843bcb', '71b36d2d6ff3', '7963cdae54e7', '7f4e269eb6f9',
        '8b601053e147', '92023abde6bc', 'adb16c4197df', 'c66f42706d9d', 'df1c566af552',
    }),
    'mensuration': frozenset({
        '1503f6f3a6ae', '264815e1d101', '303780b23d4e', '3325a11a76b5', '4c0c374833fc',
        '4df8a7f5572e', '5602bf882f5d', '5b5cffb36764', '6bdfa7c2f363', '7f0ae1b06743',
        '9d49c551a49a', 'a3f1f575328f', 'b37d8fa193dd', 'ba2842c89804', 'bc3c5d56420b',
        'c6671c01bdb5', 'ca01635809c6', 'cff2a5382636',
    }),
    'bearings': frozenset({
        '063d100b9c66', '071a75ce1ed2', '0fbf9bea334a', '2b0fb6295ba4', '2ce353347cfd',
        '300494877bfb', '496ea3eacb9e', '4fcfa4747799', '8207977e52fd', 'a28f9ce7863b',
        'ad8a12cdb230', 'b89579cfe00e', 'bad4fc2267fd', 'bd0b36e8e801', 'c74bf642c05d',
        'c777a259d3d6', 'e44711f668fa', 'eb3e3b638e5a',
    }),
    'trigonometry': frozenset({
        '0ce6a30f37d9', '2383102f84e0', '44b1476f6ef1', '4955f0684fe7', '645ecc6c79b3',
        '6b871d529a0a', '74b0c6a3fb7c', '74b5d9001f35', 'affe6d8ffa4a', 'd1609bb6b58b',
        'd5c271303b47', 'e747319c3334', 'e8537eb33269', 'f201e85aaa3b', 'ff41b25457e7',
    }),
    'algebra': frozenset({
        '13dad57dd7e9', '14769f569561', '246130852f96', '2b62f347a3e9', '2fc38e7e05bc',
        '40f2db08ad9a', '461e13da155c', '56117d825f6c', '6fe013163a85', '74e4c734fbed',
        '7ef22be66291', '9e035c8c8e3f', 'a3f9acd9de37', 'a4c885644fc2', 'e394d28c8ec2',
        'ef421a715cca', 'f7f4fba9ffcb', 'fad343f9339e', 'fba129a022fa',
    }),
    'equations_inequalities': frozenset({
        '0df4b5b366bf', '116870fea915', '24d320986a1f', '25251fe5bad2', '30ada404a608',
        '3636b076ce66', '3bda85e52799', '3e3ca8e8bfc7', '5715064775f3', '6ba223c4a238',
        '759664658cbf', 'ce3d9e2d9855', 'd67e3038e363', 'e1b6539b61e6', 'edfb0f82eb27',
    }),
    'sequences': frozenset({
        '110c3ec7f1a1', '1ad5cbb2503e', '4e796a6325a4', '52c530a4f7f0', '6a40da80e363',
        '6c7eb074424b', '7ceaf686ab6d', '7dc5ceadc8ad', '7fb5abc3b228', '83d6299edd38',
        '9434f1bdd098', '9e83dff51dff', 'b4ff7602e4bc', 'b674064fe029', 'be4f8e44dd4a',
        'cfa97e4876b6', 'fb134107cd78', 'fc7140e93aac',
    }),
    'simultaneous_equations': frozenset({
        '0b8800279556', '320bd27c5745', '48dc92ef5f05', '555c3eec06b1', '868fa030b6f8',
        '8fc0ba79942f', 'd09214678733', 'da21e3ef3a6c', 'edfb0f82eb27', 'f9b02235d17b',
    }),
    'surds': frozenset({
        '077c1fbc65fd', '0a4fd9c74612', '13a2ca2acb03', '15fbb63dfb30', '19b36b93e868',
        '2f65dbe37563', '3d63037f4925', '56dd598839e6', '650fc3aa68dd', '66a73fcf79ea',
        '6be565420193', '822ccdfca769', '982582d63c8d', '988e94464cbc', 'ae311f812a99',
        'b5e2ea5acecb', 'db974b36ca26', 'dda1671504d8', 'fc8a8ffd985a',
    }),
    'geometry_angles': frozenset({
        '20dcf8ce3fc5', '2f1455a843bf', '433aa3f9537f', '55d5afabe4f3', '5b74d2770c35',
        '7c3af4f11fcb', '9485e7ad5ed1', 'a3deaf1cc4a4', 'a7389c6c43d6', 'a88d92c681f6',
        'd1bef5fd01ed', 'd62df6091868', 'e94d5de2ef65', 'f36a5edd860f', 'fdc85f5c9575',
    }),
    'transformations': frozenset({
        '26ae5054fad2', '423b0a33bcbe', '50b8e2bc28ba', '67e074311bc1', '7bc1f614251e',
        '7bfbdbe99944', '813cd1ba30ed', '8e6eb7b34c18', 'a9368b1e8f04', 'bc04425ff54f',
        'befe5a41675b', 'c762b200bc6a', 'd73086105df7', 'f4faf6e386cd', 'ff6d24d02cbf',
    }),
    'similarity_congruence': frozenset({
        '06a4f43b37b4', '0e569f447ac2', '2c730122fd3e', '3edbfbcf66fa', '497512b19b51',
        '52e3b9218ae5', '6ae9a944a425', '70dfee339b2c', '75c75c9d6929', '7a339c7e19cd',
        '95846da11cd7', '9cdf54b285b2', 'c73b59ce358e', 'd15198809ada', 'e962d354fc23',
    }),
    'circle_theorems': frozenset({
        '0dd640d9742a', '0edc32b7cf96', '23dc59c3751d', '3be3e50b2e2e', '3f77f9f65490',
        '4c401761a980', '52adf49854d5', '59d6a5c4a2db', '5f5fc9064e38', '688b44c90948',
        '8bbf3fab178f', '8bcfab6327cb', '8f5dce770721', '8fd1117984c9', '94333f236935',
        'a07fc1e39dde', 'ad0d97311e62', 'b560aa784220', 'b6fa71f644f6', 'c2811ec8b3ab',
        'd13931e539a6', 'e2fdd3778a05', 'ebacfae4638b', 'f25cfcad386b',
    }),
    'constructions_loci': frozenset({
        '0316bc38607f', '1b50d0522e9d', '21cf0d9d5c1e', '39fe133be803', '44e393f99df9',
        '487c7828b397', '5d9cdf21e4ce', '852f2a72edd4', '9ff174a302c5', 'aa47f1d3264c',
        'c0446fea7f9a', 'ceaab716098a', 'cfc695431cea', 'e084d2fc883a', 'f3f3040bb606',
    }),
    'vectors': frozenset({
        '410188067c8e', '496ad8a7cb8d', '49b5236d46d8', '962e484f56e3', '9c2be257122c',
        'a412248e9b27', 'c6b92481c9bd', 'cf34ab60b0f7', 'cfdc4a0e232d', 'db018bc947bc',
    }),
}
