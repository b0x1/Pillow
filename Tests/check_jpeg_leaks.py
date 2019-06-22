from .helper import unittest, PillowTestCase, hopper
from io import BytesIO
import sys

iterations = 5000


"""
When run on a system without the jpeg leak fixes,
the valgrind runs look like this.

valgrind --tool=massif python test-installed.py -s -v Tests/check_jpeg_leaks.py

"""


@unittest.skipIf(sys.platform.startswith("win32"), "requires Unix or macOS")
class TestJpegLeaks(PillowTestCase):

    """
pre patch:

    MB
31.62^                                                                       :
     |                                                              @:@:@:@#::
     |                                                     @:@:@@:@:@:@:@:@#::
     |                                             ::::::::@:@:@@:@:@:@:@:@#::
     |                                   :::::@::::::: ::::@:@:@@:@:@:@:@:@#::
     |                          @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |               ::::::@::::@:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |          ::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |         :::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |        ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |        ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |      ::::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |      : ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |     @: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |    @@: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |   :@@: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     |   :@@: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     | :@:@@: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     | :@:@@: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
     | :@:@@: ::::::::: : :@: : @:::::::::::::@: : ::: ::::@:@:@@:@:@:@:@:@#::
   0 +----------------------------------------------------------------------->Gi
     0                                                                   8.535


post-patch:

    MB
21.03^          :::@@:::@::::@@:::::::@@::::::::@::::::::::::@:::@:::::::@::::
     |         #:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |         #:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |        :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |        :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |        :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |      :::#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |      : :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |      : :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |     @: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |    @@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |    @@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |    @@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |   :@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     |   :@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     | :@:@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     | :@:@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     | :@:@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     | :@:@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
     | :@:@@: :#:::@ :::@::::@ : :: : @ :::::: :@:: ::: :::: @:: @:::::::@::::
   0 +----------------------------------------------------------------------->Gi
     0                                                                   8.421

"""

    def test_qtables_leak(self):
        im = hopper("RGB")

        standard_l_qtable = [
            int(s)
            for s in """
            16  11  10  16  24  40  51  61
            12  12  14  19  26  58  60  55
            14  13  16  24  40  57  69  56
            14  17  22  29  51  87  80  62
            18  22  37  56  68 109 103  77
            24  35  55  64  81 104 113  92
            49  64  78  87 103 121 120 101
            72  92  95  98 112 100 103  99
            """.split(
                None
            )
        ]

        standard_chrominance_qtable = [
            int(s)
            for s in """
            17  18  24  47  99  99  99  99
            18  21  26  66  99  99  99  99
            24  26  56  99  99  99  99  99
            47  66  99  99  99  99  99  99
            99  99  99  99  99  99  99  99
            99  99  99  99  99  99  99  99
            99  99  99  99  99  99  99  99
            99  99  99  99  99  99  99  99
            """.split(
                None
            )
        ]

        qtables = [standard_l_qtable, standard_chrominance_qtable]

        for _ in range(iterations):
            test_output = BytesIO()
            im.save(test_output, "JPEG", qtables=qtables)

    def test_exif_leak(self):
        """
pre patch:

    MB
177.1^                                                                       #
     |                                                                    @@@#
     |                                                                :@@@@@@#
     |                                                             ::::@@@@@@#
     |                                                         ::::::::@@@@@@#
     |                                                     @@::::: ::::@@@@@@#
     |                                                  @@@@ ::::: ::::@@@@@@#
     |                                               @@@@@@@ ::::: ::::@@@@@@#
     |                                           @@::@@@@@@@ ::::: ::::@@@@@@#
     |                                        @@@@ : @@@@@@@ ::::: ::::@@@@@@#
     |                                   @@@@@@ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |                                @@@@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |                            @::@@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |                        ::::@: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |                     :@@: : @: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |                ::@@::@@: : @: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |            @@::: @ ::@@: : @: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |         @::@ : : @ ::@@: : @: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |      :::@: @ : : @ ::@@: : @: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
     |   @@@:: @: @ : : @ ::@@: : @: @@ @@ @@ @ @@ : @@@@@@@ ::::: ::::@@@@@@#
   0 +----------------------------------------------------------------------->Gi
     0                                                                   11.37


post patch:

    MB
21.06^        ::::::::::::::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |      ##::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |      # ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |      # ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |      # ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |     @# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |     @# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |     @# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |     @# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |    @@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |   @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |   @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |   @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |   @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     |   @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     | @@@@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     | @ @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     | @ @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     | @ @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
     | @ @@@# ::: ::::: : ::::::::::@::::@::::@::::@::::@::::@:::::::::@::::::
   0 +----------------------------------------------------------------------->Gi
     0                                                                   11.33

"""
        im = hopper("RGB")
        exif = b"12345678" * 4096

        for _ in range(iterations):
            test_output = BytesIO()
            im.save(test_output, "JPEG", exif=exif)

    def test_base_save(self):
        """
base case:
    MB
20.99^           :::::         :::::::::::::::::::::::::::::::::::::::::::@:::
     |         ##: : ::::::@::::::: :::: :::: : : : : : : :::::::::::: :::@:::
     |         # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |         # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |         # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |       @@# : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |       @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |       @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |     @@@ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |     @ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |    @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |    @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |    @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |    @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     |    @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     | :@@@@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     | :@ @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     | :@ @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     | :@ @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
     | :@ @@ @ # : : :: :: @:: :::: :::: :::: : : : : : : :::::::::::: :::@:::
   0 +----------------------------------------------------------------------->Gi
     0                                                                   7.882
"""
        im = hopper("RGB")

        for _ in range(iterations):
            test_output = BytesIO()
            im.save(test_output, "JPEG")


if __name__ == "__main__":
    unittest.main()
