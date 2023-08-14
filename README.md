# P2P_network_structure - P2P File Sharing System
Abstract
This project implements a peer-to-peer (P2P) file sharing system using Python. The system enables users to share and download data chunks over a decentralized network. It offers functionalities for hosting files, broadcasting chunk availability, downloading chunks, and reconstructing files from downloaded chunks.

Introduction
In this project, we have designed a P2P server and client structure for trading data chunks. While the initial focus was on JPG files, the system can be adapted to work with various data formats. Unlike traditional file sharing systems, our network overcomes barriers imposed by file sizes, offering a scalable and efficient solution.

Features
Host and share files in a P2P network.
Download data chunks from available peers.
Reconstruct complete files from downloaded chunks.
Utilize multicast-based broadcasting for improved network efficiency.
Command-line interface for user-friendly interaction.

Implementation Details
The project is implemented in Python and consists of the following components:
Data Chunking: Automatically splits hosted files into manageable data chunks.
Chunk Announcer: Periodically broadcasts the availability of data chunks to the network.
Chunk Uploader: Provides requested chunks to peers upon connection.
Chunk Downloader: Downloads specified data chunks from peers.
File Stitching: Reconstructs original files from downloaded chunks.
User Interaction: Offers a command-line interface for users to interact with the network.

Prerequisites:
Python 3.x
Hamachi
