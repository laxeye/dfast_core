# DFAST - DDBJ Fast Annotation and Submission Tool
DFAST is a flexible and customizable pipeline for prokaryotic genome annotation as well as data submission to the INSDC. It is originally developed as the background engine for the [DFAST web service](https://dfast.ng.ac.jp) and is also available as a stand-alone command-line tool.
The stand-alone version of DFAST is also refered to as DFAST-core to differentiate it from its on-line version.  
For inquiry and request, please contact us at `dfast @ nig.ac.jp`.

#### Contents
* [Overview](#overview)
* [Installation](#installation)
* [How to run](#howto)
* [Default workflow](#workflow)
* [Options](#options)
* [Citation](#citation)

## <a id="overview"></a>Overview
* **Easy install**  
DFAST is implemented in Python and runs on Mac and Linux. No additional modules are required other than BioPython. It comes with external binaries for the default workflow.
* **Flexible and customizable**  
You can customize the pipeline as you like by specifying parameters, gene prediction tools, and reference databases in the configuraition file.
Each of annotation processes is defined as a Python module with common interfaces,
which facilitates future development and incorporation of new tools.
* **Fast and rich annotation**  
DFAST can annotate a typical-sized bacterial genome within several minutes. In addition to the conventional homology search, it features unique functions such as orthologous gene assignment between reference genomes, pseudo/frameshifted gene prediction, and conserved domain search.
* **INSDC submission**  
As its name suggested, DFAST is intended to support rapid genome submission to the INSDC, especially through DDBJ. DFAST generates submission files for DDBJ Mass Submission System (MSS) as well as .tbl and .fsa file for GenBank tbl2asn.

## <a id="installation"></a>Installation
### Prerequisites
* **Python (3.4- or 2.7)**  
  DFAST is developed in Python 3.6 and runs both on Python 3.4 or later and Python 2.7.
* **BioPython package**
  You can install this with the Python package management tool `pip`:  
  ```
  (sudo) pip install biopython
  ``` 
  If `pip` is not available, please follow the [instruction](http://biopython.org/wiki/Download) of BioPython.
* **'Futures' and 'six' packages (Required only on Python 2.7)**  
DFAST uses the `concurrent.futures` module for multiprocessing and the `six` module for compatibility with Python 2 and 3. To run on Python 2.7, you need to install them:
  ```
  (sudo) pip install futures six
  ```
* **Perl and Java**  
Some of the external programs called from DFAST depend on Perl or Java. Basically, they work with the pre-installed versions on your system.  
For **RedHat/CentOS/Fedora**, the Time::Piece module should be installed:
  ```
  sudo yum install perl-Time-Piece
  ```

### Source code
Download the stable version from our web site or clone the latest version from GitHub.
* **Download the distribution**  
Download the DFAST distribution from [our site](https://dfast.nig.ac.jp/distribution), then unarchive it.
  ```
  wget https://dfast.nig.ac.jp/dfc/distribution/dfast_core_x.x.x.tar.gz  
  tar xvfz dfast_core_x.x.x.tar.gz  
  cd dfast_core_x.x.x    # Hereafter, we call this directory $DFAST_APP_ROOT
  ```
* **GitHub**
  ```
  git clone https://github.com/nigyta/dfast_core.git
  cd dfast_core    # Hereafter, we call this directory $DFAST_APP_ROOT
  ```

For your convenience, add $DFAST_APP_ROOT in your `PATH`.
```
export PATH=$DFAST_APP_ROOT:$PATH
```

### Reference databases
  After downloading/cloning the source code, prepare reference databases using the bundled utility script.
1. **Default protein database**
    ```
    python scripts/file_downloader.py --protein dfast
    ```
    File downloading and database indexing for GHOSTX/Z and BLASTP will be performed.
2. **HMMer and RPS-BLAST databases (this may take time)**
    ```
    python scripts/file_downloader.py --cdd Cog --hmm TIGR
    ```
    DFAST default workflow requires COG database for RPS-BLAST and TIGRFAM database for hmmerscan.
* **See help for more information.**
    ```
    python scripts/file_downloader.py -h
    ```
## <a id="howto"></a>How to run
1. **Help**  
    Make sure that $DFAST_APP_ROOT has been added to your `PATH`.
    ```
    dfast -h
    ```
    or by specifying the Python interpreter,
    ```
    python $DFAST_APP_ROOT/dfast -h
    ```

2. **Test run**  
    ```
    dfast --config $DFAST_APP_ROOT/example/test_config.py
    ```
    This minimum workflow includes CDS prediction and database search against the default protein database using the GHOSTX aligner. The result will be generated in `RESULT_TEST` dierctory.  
    If not working properly, please check if the default database is installed. Normally, it finishes within a minute.

3.  **Basic usage**  
    ```
    dfast --genome path/to/your_genome.fna
    ```
    This invokes the DFAST pipeline with the default workflow defined in $DFAST_APP_ROOT/dfc/default_config.py. DFAST accepts a FASTA-formatted genome sequence file as a query.  
4. **Advanced usage**  
    By providing command line options, you can override the default settings described in the configuration file.
    ```
    dfast --genome your_genome.fna --organism "Escherichia coli" --strain "str. xxx" --locus_tag_prefix ECXXX --minimum_length 200 --reference EC_ref_genome.gbk --aligner blastp --out OUT_ECXXX
    ```
    `locus_tag_prefix` is required if you want your genome to be submitted to the INSDC. DFAST generates DDBJ and GenBank submission files. For more information, please refer to [INSDC submission](docs/insdc_submission.md).
     If you set `--references` option, OrthoSearch (orthologous gene assignment) is enabled, which conducts all-against-all protein alignments between given reference genomes to infer orthologous genes.  
     `--aligner blastp` will let DFAST use BLASTP for protein alignments instead of default GHOSTX.

     These optional values can be specified in a configuration file, saving you from providing them as command line options. See the following step. 
5. **More advanced usage: Creating your own workflow**  
An easy way to do this is to copy and edit the default configuration file, which is located in $DFAST_APP_ROOT/dfc/default_config.py.
The configuration file is a self-explanatory Python script, in which the workflow is defined using basic Python objects like lists and dictionaries.

    You can call your original configuration file with the `--config` option.
    ```
    dfast --genome your_genome.fna --config your_config.py
    ```

## <a id="workflow"></a>Default workflow
DFAST default annotation workflow accepts a genomic FASTA file (draft or complete) as an input and includes following processes. Read [Workflow](docs/workflow.md) to learn more.

### Structural annotation
The following tools are run in parallel to predict biological features (e.g. CDSs and RNAs). After that, partial and overlapping features will be cleaned up.
* CDS prediction (MetaGeneAnnotator)
* rRNA prediction (Barrnap)
* tRNA/tmRNA prediction (Aragorn)
* CRISPR prediction (CRT)
* Assembly gaps within sequences

### Functional annotation
1. OrthoSearch (Optional. Set `--references` option to enable this.)
2. DBsearch using the Ghostx aligner against the DFAST default database
3. PseudoGeneDetection (internal stop codons and frameshifts)
4. HMMscan against the profile HMM database of TIGRFAM
5. CDDsearch against COG database from NCBI Conserved Domain Database

### Output
* Sequence and annotation data in GFF3 and GenBank format
* Sequence data in FASTA format
* Statistics for genome sequences and annotated features
* DDBJ and GenBank submission files

## <a id="options"></a>Options

```  
Basic options:
  -g PATH, --genome PATH
                        Genomic FASTA file
  -o PATH, --out PATH   Output directory
  -c PATH, --config PATH
                        Configuration file
  --organism STR        Organism name
  --strain STR          Strain name

Genome settings:
  --complete BOOL       Treat the query as a complete genome. Not required
                        unless you need INSDC submission files. [t|f]
  --use_original_name BOOL
                        Use original sequence names in a query FASTA file
                        [t|f]
  --sort_sequence BOOL  Sort sequences by length [t|f]
  --minimum_length INT  Minimum sequence length

Locus_tag settings:
  --prefix STR          Locus tag prefix
  --step INT            Increment step of locus tag
  --use_separate_tags BOOL
                        Use separate tags according to feature types [t|f]

Workflow options:
  --references PATH     Reference file(s) for OrthoSearch. Use semicolons for
                        multiple files, e.g. 'genome1.faa;genome2.gbk'
  --aligner STR         Aligner to use [ghostx|ghostz|blastp]

Genome source modifiers and metadata [advanced]:
  These values are only used to create INSDC submission files and do not
  affect the annotation result. See documents for more detail.

  --seq_names STR       Sequence names for each sequence (for complete genome)
  --seq_types STR       Sequence types for each sequence (chromosome/plasmid,
                        for complete genome)
  --seq_topologies STR  Sequence topologies for each sequence
                        (linear/circular, for complete genome)
  --additional_modifiers STR
                        Additional modifiers for source features
  --metadata_file PATH  Path to a metadata file (Optional for DDBJ submission
                        file)
  --center_name STR     Genome center name (Optional for GenBank submission
                        file)

Run options:
  --cpu INT             Number of CPUs to use
  --force               Force overwriting output
  --debug               Run in debug mode (Extra logging and retaining
                        temporary files)
  --show_config         Show pipeline configuration and exit
  --version             Show program version
  -h, --help            Show this help message
```
## <a id="distribution"></a>Software distribution
DFAST is freely available as open-source under the GPLv3 license (See [LICENSE](docs/LICENSE)).

This distribution contains following external programs.
* [MetaGeneAnnotator](http://metagene.cb.k.u-tokyo.ac.jp/) (© Hideki Noguchi)
 Redistributed by courtesy of Hideki Noguchi at National Institute of Genetics.
* [Aragorn](http://mbio-serv2.mbioekol.lu.se/ARAGORN/) (GPLv3)
* [Barrnap](https://github.com/tseemann/barrnap) (GPLv3)
* [CRT](http://www.room220.com/crt/) (Public domain)
* [GHOSTX](http://www.bi.cs.titech.ac.jp/ghostx/) (BSD-2-Clause)
* [GHOSTZ](http://www.bi.cs.titech.ac.jp/ghostz/) (CC BY 4.0)
* blastp, makeblastdb, blastdbcmd, rpsblast, rpsbproc from [NCBI-BLAST+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download) package. (Public domain)
* hmmpress, hmmscan from [HMMer](http://hmmer.org/) package (GPLv3)
* [LAST](http://last.cbrc.jp/) (GPLv3)

## <a id="citation"></a>Citation
* on-line version of DFAST  
    DFAST and DAGA: web-based integrated genome annotation tools and resources  
    *Biosci Microbiota Food Health*. 2016; 35(4): 173–184.  
    Yasuhiro TANIZAWA, Takatomo FUJISAWA, Eli KAMINUMA, Yasukazu NAKAMURA, and Masanori ARITA
* stand-alone version (DFAST-core)  
    Manuscript in preparation.

