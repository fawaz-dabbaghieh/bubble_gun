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
* A user wants to only detect the bubble chains and output JSON file with information about the bubbles and low memory usage. Command: `./main.py -g test.gfa -k 51 bchains --bubble_json test.json --save_memory`. With saving memory, only the graph topology will be stored in memory and the sequences will not be read from the file. (NOTED: JSON functionality is under construction still)
* A user wants to only detect the bubble chains and output a new GFA graph with only the bubble chains. Command: `./main.py -g test.gfa -k 51 bchains --chains_gfa chains_output.gfa`
* A user wants to detect bubble chains, output a JSON file, a GFA file with only chains and a FASTA file with only bubble branches sequences, where the sequence name indicate from which chains and which bubble they come. Command: `./main.py -g test.gfa -k 51 bchains --bubble_json test.json --chains_gfa chains_output.gfa --fasta test_output.fasta`
