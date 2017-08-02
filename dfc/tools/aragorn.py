#! /usr/bin/env python
# coding: UTF8

from .base_tools import StructuralAnnotationTool
from ..models.bio_feature import ExtendedFeature


class Aragorn(StructuralAnnotationTool):
    """
    Aragorn class extended from StructuralAnnotationTool class

    Tool type: tRNA and tmRNA prediction
    URL: http://mbio-serv2.mbioekol.lu.se/ARAGORN/Downloads/
    REF: https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gkh152

    """
    version = None
    TYPE = "tRNA"
    NAME = "Aragorn"
    VERSION_CHECK_CMD = ["aragorn", "-h"]
    VERSION_PATTERN = r"ARAGORN v(.+) Dean Laslett"

    def __init__(self, options=None, workDir="OUT"):
        """
        aragorn options:
            -l: for linear sequences, -c: for circular sequences
            -w: print out batch mode
            -o: outfile
            -gcbact for Bacterial/Plant Chloroplast genetic code, "-gcstd" for standard genetic code.
        :param options:
        :param workDir:
        """
        super(Aragorn, self).__init__(options, workDir)
        self.gcode = options.get("gcode", "-gcbact")
        self.cmd_options = options.get("cmd_options", "-l")

    def getCommand(self):
        """
        "aragorn -l -gc$gcode $aragorn_opt -w \Q$outdir/$prefix.fna\E"; # -t/-m
        -l : for linear sequence,  -c : for circular sequence
        """
        cmd = ["aragorn", self.gcode, self.cmd_options, "-w", "-o", self.outputFile, self.genomeFasta]
        return cmd

    def getFeatures(self):

        def _parseResult():
            with open(self.outputFile) as f:
                # Example of an output
                # "5   tRNA-Leu              c[100903,100988]      36      (caa)"
                # "1   tmRNA                 c[61802,62165]        88,126  AKNSNKTYAFAA*"
                for line in f:
                    if line.startswith(">"):
                        sequence = line.strip().replace(">", "")
                        skipFlag = True
                    elif skipFlag:
                        # skip the subsequent line of the header
                        skipFlag = False
                    else:
                        num, product, location, anticodon_position, anticodon = line.split()
                        if location.startswith("c"):
                            strand = -1
                            location = location[1:]  # remove leading "c" c[100903,100988] -> [100903,100988]
                        else:
                            strand = 1
                        left, right = location[1:-1].split(",")
                        # for tmRNA, anticodon represents peptide sequence,
                        # anticodon_position represents translated region
                        yield sequence, product, left, right, strand, anticodon, anticodon_position

        D = {}
        i = 0
        for sequence, product, left, right, strand, anticodon, anticodon_position in _parseResult():

            location = self.getLocation(left, right, strand)
            i += 1
            if product == "tmRNA":
                type_ = "tmRNA"
                product = "transfer-messenger RNA"
                annotations = {"tag_peptide_translated_region": anticodon_position,
                                       "tmRNA_tag_peptide": anticodon.replace("*", ""),
                                       }
            else:
                type_ = "tRNA"
                annotations = {"anticodon_position": anticodon_position,
                                       "anticodon": anticodon[1:-1],  # remove leading "(" and trailing ")"
                                       }
            feature = ExtendedFeature(location=location, type=type_, id="{0}_{1}".format(self.__class__.__name__, i),
                                      seq_id=sequence, annotations=annotations)
            feature.qualifiers = {
                "product": [product],
                # "inference": ["identified by {0}".format(self.__class__.NAME).strip()],
                "inference": ["COORDINATES:profile:{0}:{1}".format(self.__class__.NAME, self.__class__.version).strip()],
            }
            D.setdefault(sequence, []).append(feature)
        return D
