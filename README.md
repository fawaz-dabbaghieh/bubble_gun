# BubbleGun
A tool for detecting Bubbles and Superbubble chains in graphs. It mainly works with GFA.
It can also compact the graph, separate biggest component, and separate neighborhood from graphs efficiently.


## Usage and Subcommands
These are the general information about the tool

```
usage: main.py [-h] [-e] [-g GRAPH_PATH] [-k K] [--with_coverage]
               [--log LOG_LEVEL]
               {bchains,compact,biggestcomp,bfs,gamdigest} ...

Find Bubble Chains.

Subcommands:
  {bchains,compact,biggestcomp,bfs,gamdigest}
                        Available subcommands
    bchains             Command for detecting bubble chains
    compact             Command for compacting graphs
    biggestcomp         Command for separating biggest component
    bfs                 Command for separating neighborhood
    gamdigest           Command for digesting a gam file

Global Arguments:
  -h, --help            show this help message and exit
  -e, --examples        prints out example commands to use the tool
  -g GRAPH_PATH, --in_graph GRAPH_PATH
                        graph file path (GFA or VG)
  -k K, --k_mer K       K value of as integer
  --with_coverage       If this option given, mean coverage is taken from the
                        GFA file
  --log LOG_LEVEL       The logging level [DEBUG, INFO, WARNING, ERROR,
                        CRITICAL]
```
As shown, it takes some Global arguments then specific subcommands.
Each subcommand will be explained in the following sections with example commands to run the tool using that subcommand.


### Subcommand bchains
This subcommand is for detecting bubbles and bubble chains and outputting results.
The following help page is available for bchains
```
usage: main.py bchains [-h] [--bubble_json OUT_JSON] [--only_simple]
                       [--save_memory] [--chains_gfa CHAINS_GFA]
                       [--fasta FASTA] [--out_haplos]

optional arguments:
  -h, --help            show this help message and exit
  --bubble_json OUT_JSON
                        Outputs Bubbles, Superbubbles, and Chains as a JSON
                        file
  --only_simple         If used then only simple bubbles are detected
  --save_memory         Identifies bubble chain with less memory. No
                        statistics outputted
  --chains_gfa CHAINS_GFA
                        Output only bubble chains as a GFA file
  --fasta FASTA         Outputs the bubble branches as fasta file (doesn't
                        work with memory saving)
  --out_haplos          output randomly two haplotypes for each chain (doesn't
                        work with memory saving)

```
Examples:
* A user wants to only detect the bubble chains and output JSON file with information about the bubbles and low memory usage. Command: `./main.py -g test.gfa -k 51 bchains --bubble_json test.json --save_memory`. With saving memory, only the graph topology will be stored in memory and the sequences will not be read from the file.
* A user wants to only detect the bubble chains and output a new GFA graph with only the bubble chains. Command: `./main.py -g test.gfa -k 51 bchains --chains_gfa chains_output.gfa`
* A user wants to detect bubble chains, output a JSON file, a GFA file with only chains and a FASTA file with only bubble branches sequences, where the sequence name indicate from which chains and which bubble they come. Command: `./main.py -g test.gfa -k 51 bchains --bubble_json test.json --chains_gfa chains_output.gfa --fasta test_output.fasta`


### Subcommand compact
This subcommand outputs a compacted GFA file. Example:

`./main.py -g test_graph.gfa -k 41 compact compacted_test.gfa`


### Subcommand biggestcomp
This subcommand separates the biggest component in the graph and output it. Example:

`./main.py -g test_graph.gfa -k 41 biggestcomp biggest_comp.gfa`


### Subcommand bfs
This subcommand can be used to extract a neighborhood using BFS around a start node or several start nodes (takes the node id), these neighborhood will be outputted as a GFA file. Examples:
* Extracting a neighborhood of size 100 nodes around the node with id 540
`./main.py -g test_graph.gfa -k 51 bfs --start 540 --neighborhood_size 100 --output_neighborhood output.gfa`
* Extracting the neighborhoods of size 100 nodes around nodes 500, 540, and 1509. Regardless if these neighborhood are connected or not, they all will be in the same output file.
`./main.py -g test_graph.gfa -k 51 bfs --start 500 540 1509 --neighborhood_size 100 --output_neighborhood output.gfa`


### Subcommand gamdigest
This command is used to "filter" a GAM file which is an alignment file of reads aligned to the graph. This mainly works on the output from [GraphAligner](https://github.com/maickrau/GraphAligner) after aligning long reads to the graph. GraphAligner outputs a GAM files which this commands takes along with the bubble chain graph aligned to and a minimum length cutoff for mappings. Each read would have several mappings, first, all mappings that are smaller than the cutoff are dicarded, then if the same read mapped to the same chain more than once, the longest mapping is kept.
The output is a pickled dictionary with keys as read names and values as a list of nodes the read have mapped to. This pickled dictionary along with the graph can be given then to Whatshap phaseb command to output phased bubbles according to how the long reads mapped to these bubbles, but this is still under construction.
