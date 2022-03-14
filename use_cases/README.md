- [Myxococcus xanthus Assemblies Use-Case](#myxococcus-xanthus-assemblies-use-case)  
  * [de Bruijn Graph](#de-bruijn-graph)  
      + [Detecting Bubble Chains](#detecting-bubble-chains)  
      + [Extracting largest connected component](#extracting-largest-connected-component)  
      + [Producing JSON of Bubble Chains](#producing-json-of-bubble-chains)  
      + [Extracting Chain(s)](#extracting-bubble-chains)  
  * [Bluntified Pangenome Graph](#bluntified-pangenome-graph)  
- [HG002 Use-Case](#hg002-use-case)  
  * [Correcting Reads](#correcting-reads)  
  * [Constructing the de Bruijn Graph](#constructing-the-de-bruijn-graph)  
  * [Processing with BubbleGun](#processing-with-bubblegun)  
      
  
# Myxococcus xanthus Assemblies Use-Case  
  
## de Bruijn Graph  
The `m_xanthus_10_assemblies.unitigs.gfa` is produced from the 10 assemblies mentioned in the supplementary materials of the paper. The assemblies were concatenated together and then given to `bcalm` to produce a de Briujn Graph with k-mer size of 41. The command used to produce the unitigs is:   
  
```$ bcalm -in m_xanthus_10_assemblies.fa -kmer-size 41 -abundance-min 1 -nb-cores 5```
  
This produced the file `m_xanthus_10_assemblies.unitigs.fa` which can be converted to a gfa file using [this script](https://github.com/GATB/bcalm/blob/master/scripts/convertToGFA.py) from `bcalm`:   
  
```$ python3 convertToGFA.py m_xanthus_10_assemblies.unitigs.fa m_xanthus_10_assemblies.unitigs.gfa 41```  
  
### Detecting Bubble Chains  
To detect bubble chains, the `bchains` subcommand was used without arguments, which will only detect bubble chains and produces some statistics:  
```  
$ BubbleGun -g m_xanthus_10_assemblies.unitigs.gfa bchains  
  
The number of Simple Bubbles is 40381  
The number of Superbubbles is 41356  
The number of insertions is 0  
Sequence coverage of the bubble chains is 91.79359052995717%  
Node coverage of the bubble chains is 94.32604093154552%  
The longest chain seq-wise has 746155 bp  
The longest chain bubble_wise has 916 bubbles  
```  
  
### Extracting largest connected component  
One can extract the biggest connected component in terms of number of nodes in the graph by using the following command:  
  
```$ BubbleGun -g m_xanthus_10_assemblies.unitigs.gfa biggestcomp m_xanthus_10_assemblies.unitigs.biggest_comp.gfa```  
### Extracting Bubble Chains  
To extract the chains into a separate GFA file, the following command can be used:  
```  
$ BubbleGun -g m_xanthus_10_assemblies.unitigs.gfa bchains --chains_gfa m_xanthus_10_assemblies.unitigs.bchains.gfa  
```  
  
To show that the new subgraph is actually only made of bubble chains. If we run BubbleGun again, we will get 100% coverage now and the same number of simple and super bubbles:  
```  
$ BubbleGun -g m_xanthus_10_assemblies.unitigs.bchains.gfa bchains  
  
The number of Simple Bubbles is 40381  
The number of Superbubbles is 41356  
The number of insertions is 0  
Sequence coverage of the bubble chains is 100.0%  
Node coverage of the bubble chains is 100.0%  
The longest chain seq-wise has 746155 bp  
The longest chain bubble_wise has 916 bubbles  
```  
  
### Producing JSON of Bubble Chains  
To produce the JSON file with all bubbles information, the following command can be used:  
  
```$ BubbleGun -g m_xanthus_10_assemblies.unitigs.gfa bchains --bubble_json m_xanthus_10_assemblies.unitigs.bchains.json```  
  
The JSON file has the following structure:  
```json  
{  
 "str_chain_id": { "chain_id": "str_chain_id", "end": ["str_start_node_id", "str_end_node_id"], "bubbles": [ { "type": "type", "id": "int_bubble_id", "ends": ["str_start_node_id", "str_end_node_id"], "inside": ["str_node_id","..."] }, { "..." }, { "..." } ], "parent_sb": "int_id", "parent_chain": "int_id" }}  
```  
So it starts with a string id of the chain, inside of that there are these keys `'chain_id', 'ends', 'bubbles', 'parent_sb', 'parent_chain'`, if this chains was not nested, then there won't be a parent sb and parent chain.  
One can for example load this JSON file into python and inspect the different chains:  
  
```python  
import json  
  
with open("m_xanthus_10_assemblies.unitigs.bchains.json", "r") as in_file:  
 bubble_chains = json.load(in_file)  
# let us for example get a list of chains ids with length of 10 bubbles  
chain_list = []  
for chain_key, chain in bubble_chains.items():  
 if len(chain['bubbles']) == 10: chain_list.append(chain_key)# chain_list will be  a list of strings that are the ids, and to get any chain, simple use that id as key  
bubble_chains['425']  
# {'chain_id': 425,  
#  'ends': ['434125', '436190'],  
#  'bubbles': [{'type': 'super',  
#    'id': 1298,  
#    'ends': ['434125', '324091'],  
#    'inside': ['130678', '291683', '271121', '340902', '20122']},  
#   {'type': 'simple',  
#    'id': 1299,  
#    'ends': ['541197', '324091'],  
#    'inside': ['454725', '485937']},  
#   {'type': 'simple',  
#    'id': 1300,  
#    'ends': ['541197', '436190'],  
#    'inside': ['144223', '255360']}],  
#  'parent_sb': 31898, #  'parent_chain': 8046}  
  
```  
  
### Extracting Chain(s)  
You can separate a certain chain using `chainout` subcommand. For example, we can extract the parent of chain 425 from the previous example,   
to see if it was actually nested:  
  
```$ BubbleGun -g m_xanthus_10_assemblies.unitigs.bchains.gfa chainout --json_file m_xanthus_10_assemblies.unitigs.bchains.json --chain_ids 8046 --output_chain chain_8046.gfa```  
  
This will produce a separate GFA file with only that parent chain which we can easily visualize in tools like Bandage or gfaviz.  
  
## Bluntified Pangenome Graph  
To show that BubbleGun also works on bluntified graphs, we constructed a pangenome from the 10 Myxococcus xanthus assemblies using minigraph. The command used was:  
  
```$ minigraph -xggs -t 2 GCA_000340515.1_Myxococcus_xanthus_DZF1_genomic.fna GCA_900106535.1_IMG-taxon_2693429903_annotated_assembly_genomic.fna GCA_000012685.1_ASM1268v1_genomic.fna GCA_000278585.2_ASM27858v2_genomic.fna GCA_006400955.1_ASM640095v1_genomic.fna GCA_006401215.1_ASM640121v1_genomic.fna GCA_006401635.1_ASM640163v1_genomic.fna GCA_006402015.1_ASM640201v1_genomic.fna GCA_006402415.1_ASM640241v1_genomic.fna GCA_006402735.1_ASM640273v1_genomic.fna > minigraph_m_xanthus_10_assemblies_pangenome.gfa ```. 
  
The graph output of minigraph has 3775 nodes and 5043 edges, and bubble gun was able to detect bubble chains in 0.4 seconds and reported:  
  
```  
$ BubbleGun -g minigraph_m_xanthus_10_assemblies_pangenome.gfa bchains  
  
The number of Simple Bubbles is 655  
The number of Superbubbles is 314  
The number of insertions is 75  
Sequence coverage of the bubble chains is 88.48293973667816%  
Node coverage of the bubble chains is 98.72847682119205%  
The longest chain seq-wise has 885640 bp  
The longest chain bubble_wise has 82 bubbles  
```  
  
  
# HG002 Use-Case  
## Correcting Reads  
First of all, the public [HG002 short reads](https://s3-us-west-2.amazonaws.com/human-pangenomics/index.html?prefix=NHGRI_UCSC_panel/HG002/hpp_HG002_NA24385_son_v1/ILMN/NIST_Illumina_2x250bps/) was used, and corrected using [Lighter](https://github.com/mourisl/Lighter), the following command was used:  
  
```  
$ lighter -r D1_S1_L001_R1_001.fastq.gz -r D1_S1_L001_R1_002.fastq.gz -r D1_S1_L001_R1_003.fastq.gz -r D1_S1_L001_R1_004.fastq.gz -r D1_S1_L001_R1_005.fastq.gz -r D1_S1_L001_R1_006.fastq.gz -r D1_S1_L001_R1_007.fastq.gz -r D1_S1_L001_R1_008.fastq.gz -r D1_S1_L001_R1_009.fastq.gz -r D1_S1_L001_R1_010.fastq.gz -r D1_S1_L001_R1_011.fastq.gz -r D1_S1_L001_R1_012.fastq.gz -r D1_S1_L001_R1_013.fastq.gz -r D1_S1_L001_R1_014.fastq.gz -r D1_S1_L001_R1_015.fastq.gz -r D1_S1_L001_R1_016.fastq.gz -r D1_S1_L001_R1_017.fastq.gz -r D1_S1_L001_R2_001.fastq.gz -r D1_S1_L001_R2_002.fastq.gz -r D1_S1_L001_R2_003.fastq.gz -r D1_S1_L001_R2_004.fastq.gz -r D1_S1_L001_R2_005.fastq.gz -r D1_S1_L001_R2_006.fastq.gz -r D1_S1_L001_R2_007.fastq.gz -r D1_S1_L001_R2_008.fastq.gz -r D1_S1_L001_R2_009.fastq.gz -r D1_S1_L001_R2_010.fastq.gz -r D1_S1_L001_R2_011.fastq.gz -r D1_S1_L001_R2_012.fastq.gz -r D1_S1_L001_R2_013.fastq.gz -r D1_S1_L001_R2_014.fastq.gz -r D1_S1_L001_R2_015.fastq.gz -r D1_S1_L001_R2_016.fastq.gz -r D1_S1_L001_R2_017.fastq.gz -r D1_S1_L002_R1_001.fastq.gz -r D1_S1_L002_R1_002.fastq.gz -r D1_S1_L002_R1_003.fastq.gz -r D1_S1_L002_R1_004.fastq.gz -r D1_S1_L002_R1_005.fastq.gz -r D1_S1_L002_R1_006.fastq.gz -r D1_S1_L002_R1_007.fastq.gz -r D1_S1_L002_R1_008.fastq.gz -r D1_S1_L002_R1_009.fastq.gz -r D1_S1_L002_R1_010.fastq.gz -r D1_S1_L002_R1_011.fastq.gz -r D1_S1_L002_R1_012.fastq.gz -r D1_S1_L002_R1_013.fastq.gz -r D1_S1_L002_R1_014.fastq.gz -r D1_S1_L002_R1_015.fastq.gz -r D1_S1_L002_R1_016.fastq.gz -r D1_S1_L002_R1_017.fastq.gz -r D1_S1_L002_R2_001.fastq.gz -r D1_S1_L002_R2_002.fastq.gz -r D1_S1_L002_R2_003.fastq.gz -r D1_S1_L002_R2_004.fastq.gz -r D1_S1_L002_R2_005.fastq.gz -r D1_S1_L002_R2_006.fastq.gz -r D1_S1_L002_R2_007.fastq.gz -r D1_S1_L002_R2_008.fastq.gz -r D1_S1_L002_R2_009.fastq.gz -r D1_S1_L002_R2_010.fastq.gz -r D1_S1_L002_R2_011.fastq.gz -r D1_S1_L002_R2_012.fastq.gz -r D1_S1_L002_R2_013.fastq.gz -r D1_S1_L002_R2_014.fastq.gz -r D1_S1_L002_R2_015.fastq.gz -r D1_S1_L002_R2_016.fastq.gz -r D1_S1_L002_R2_017.fastq.gz -t 30 -K 21 6000000000 &  
```  
  
## Constructing the de Bruijn Graph  
1- The resulting corrected files are concatenated and the de Bruijn Graph was constructed using [bcalm2](https://github.com/GATB/bcalm) with the following command on the corrected reads:  
  
```  
$ bcalm -nb-cores 40 -in all_reads.cor.fq.gz -kmer-size 61 -abundance-min 3  
```  
  
2- The `bcalm` command will generate a fasta file with unitigs that can be turned into a graph file in GFA format using [this script](https://github.com/GATB/bcalm/blob/master/scripts/convertToGFA.py), with the following command:   
  
```  
$ python3 convertToGFA.py all_reads.cor.fq.unitigs.fa all_reads.cor.fq.unitigs.gfa 61  
```  
  
3- Tips were removed using the UntipRelative.cpp from [GraphAligner](https://github.com/maickrau/GraphAligner), the following command was used:  
  
```$ ./UntipRelative 100 200 0.05 < all_reads.cor.fq.unitigs.gf > HG002_short_reads_k61_unitigs_untipped.gfa ```
  
## Processing with BubbleGun  
The file `HG002_short_reads_k61_unitigs_untipped.gfa` is uploaded [here](https://zenodo.org/record/6351721#.Yi8_in-ZMQ9) and the user can use to test `BubbelGun` with.  
  
1- First thing we need to do is to compact the graph, as removing some tips might have generated linear stretches of nodes that can be compacted, the following copmmand is used:  
  
```  
$ BubbleGun -g HG002_short_reads_k61_unitigs_untipped.gfa compact HG002_short_reads_k61_unitigs_untipped.compacted.gfa  
```  
  
2- Now that the graph is compacted, we can detect bubbles and produce the bubbles information json file and a text file with simple stats about the bubbles using the following command:  
  
```  
$ BubbleGun -g HG002_short_reads_k61_unitigs_untipped.compacted.gfa bchains --bubble_json hg002_bubbles.json > hg002_bubbles_stats.txt  
```  
  
3- To validate the simple bubbles and compare them to the GIAB high-confidence variants, we used [this](https://bitbucket.org/jana_ebler/vcf-merging/src/chains-genotyping/) Snakemake pipeline that takes two FASTA file where each haplotype is in a file. To produce such haplotypes from simple bubbles chains using `BubbleGun` the following command was used:  
  
```  
$ BubbleGun -g HG002_short_reads_k61_unitigs_untipped.compacted.gfa bchains --only_simple --out_haplos  
```  
  
Where this command will produce two FASTA files named `haplotype1.fasta` and `haplotype2.fasta`, where each chain of simple bubbles is split into two complementary linear paths (two haplotypes) and outputted into the fasta files.  
  
4- To use the Snakemake pipeline to produce variants, [this](https://bitbucket.org/jana_ebler/vcf-merging/src/chains-genotyping/) Snakemake pipeline is used, and the user just need to provide a reference and the two haplotype FASTA files produced in the config file, example `config.json`:  
  
```json  
{
	"reference": 
		{
			"filename": "GRCh38_full_analysis_set_plus_decoy_hla.fa",
			"prefix": "chr"
		},
	"assemblies":
		{
			"sample1" : ["abundance_min_3/haplotype1.fasta", "abundance_min_3/haplotype2.fasta"]
		},
	"trios":
		{
		},
	"scripts": "scripts",
	"outdir" : "merged/"
}
```