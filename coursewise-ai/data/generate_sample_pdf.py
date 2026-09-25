import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

def create_sample_course_pdf():
    output_dir = Path(__file__).resolve().parent
    output_path = output_dir / "sample_dense_technical_course.pdf"
    
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    
    # PAGE 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, height - 60, "CS801: Advanced Distributed Systems & Consensus Protocols")
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(54, height - 80, "Department of Computer Science & Engineering - Technical Lecture Notes")
    c.setLineWidth(1)
    c.line(54, height - 90, width - 54, height - 90)
    
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, height - 120, "1. Foundations of Distributed Systems")
    
    c.setFont("Helvetica", 10)
    p1 = (
        "A distributed system is defined as a collection of autonomous computing entities (nodes) "
        "that communicate over a shared network to coordinate actions and share resources. Unlike centralized "
        "architectures, distributed environments inherently face partial failures, asynchronous network latencies, "
        "and lack of a globally synchronized physical clock. As defined by Lamport, a distributed system is one "
        "in which the failure of a computer you didn't even know existed can render your own computer unusable."
    )
    y = height - 145
    for line in [p1[i:i+85] for i in range(0, len(p1), 85)]:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "1.1 The CAP Theorem and Consistency Models")
    y -= 30
    p2 = (
        "Formulated by Eric Brewer and formally proved by Seth Gilbert and Nancy Lynch, the CAP theorem states "
        "that any distributed data store can simultaneously provide at most two of the following three guarantees: "
        "Consistency (every read receives the most recent write or an error), Availability (every non-failing node "
        "returns a non-error response), and Partition Tolerance (the system continues to operate despite arbitrary "
        "packet drops or network partitioning). Under real-world physical networks where partitions are inevitable, "
        "system designers must choose between CP (consistent under partition) and AP (available under partition)."
    )
    for line in [p2[i:i+85] for i in range(0, len(p2), 85)]:
        c.drawString(54, y, line)
        y -= 14
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "1.2 Linearizability vs Sequential Consistency")
    y -= 30
    p3 = (
        "Linearizability refers to a strong recency guarantee where operations appear to take effect instantaneously "
        "at a specific point in real time between their invocation and response. Sequential consistency, by contrast, "
        "relaxes real-time ordering and requires only that all processes agree on a single global sequence of operations "
        "that preserves each process's local program order."
    )
    for line in [p3[i:i+85] for i in range(0, len(p3), 85)]:
        c.drawString(54, y, line)
        y -= 14
        
    c.setFont("Helvetica", 9)
    c.drawString(width / 2 - 40, 36, "CourseWise AI Reference Document - Page 1")
    c.showPage()
    
    # PAGE 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, height - 60, "2. The Consensus Problem and FLP Impossibility")
    c.line(54, height - 70, width - 54, height - 70)
    
    c.setFont("Helvetica", 10)
    y = height - 95
    p4 = (
        "Consensus is defined as the core coordination primitive whereby distributed nodes agree upon a single "
        "data value or sequence of state machine transitions. A consensus protocol must satisfy three correctness "
        "properties: Agreement (all non-faulty nodes decide the same value), Validity (the decided value must have "
        "been proposed by some node), and Termination (all non-faulty nodes eventually decide a value)."
    )
    for line in [p4[i:i+85] for i in range(0, len(p4), 85)]:
        c.drawString(54, y, line)
        y -= 14
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "2.1 The FLP Impossibility Result")
    y -= 30
    p5 = (
        "The landmark theorem proved by Fischer, Lynch, and Paterson (1985) establishes that in an asynchronous "
        "network model, no deterministic consensus protocol can guarantee termination in the presence of even a single "
        "unannounced crash failure. Because message delivery delays are unbounded, a node cannot distinguish between "
        "a failed node and an exceptionally slow network connection. Consequently, real-world consensus protocols "
        "such as Paxos, Raft, and PBFT make partial synchrony assumptions or use randomized timeouts."
    )
    for line in [p5[i:i+85] for i in range(0, len(p5), 85)]:
        c.drawString(54, y, line)
        y -= 14
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "2.2 Foundational Prerequisites")
    y -= 30
    p6 = (
        "To understand consensus mechanisms, students require prior mastery of several foundational concepts: "
        "Discrete Mathematics (graph structures and partial orders), Network Sockets (TCP packet transmission, "
        "sliding windows, and retransmission timeouts), and State Machine Replication (formal deterministic "
        "automata transitioning across identical logs)."
    )
    for line in [p6[i:i+85] for i in range(0, len(p6), 85)]:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica", 9)
    c.drawString(width / 2 - 40, 36, "CourseWise AI Reference Document - Page 2")
    c.showPage()
    
    # PAGE 3
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, height - 60, "3. Raft Consensus: Architecture and Decomposition")
    c.line(54, height - 70, width - 54, height - 70)
    
    c.setFont("Helvetica", 10)
    y = height - 95
    p7 = (
        "Designed by Ongaro and Ousterhout at Stanford University, Raft decomposes consensus into three independent "
        "sub-problems: Leader Election, Log Replication, and Safety invariants. Nodes in Raft exist in one of three "
        "states: Follower, Candidate, or Leader. Time is divided into discrete Terms numbered with monotonic integers."
    )
    for line in [p7[i:i+85] for i in range(0, len(p7), 85)]:
        c.drawString(54, y, line)
        y -= 14
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "3.1 Leader Election and Randomized Heartbeats")
    y -= 30
    p8 = (
        "When followers experience heartbeat timeout, they increment their term and transition to candidate status, "
        "broadcasting RequestVote RPCs. To prevent split-vote scenarios where multiple candidates split the quorum, "
        "Raft employs randomized election timeouts (e.g., 150ms to 300ms). A candidate wins the election once it "
        "receives votes from a strict majority quorum of (N/2 + 1) nodes."
    )
    for line in [p8[i:i+85] for i in range(0, len(p8), 85)]:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "3.2 Log Matching and State Machine Invariant")
    y -= 30
    p9 = (
        "Log replication occurs via AppendEntries RPCs. If two entries in different logs have the same index and term, "
        "they store the same command, and their logs are identical in all preceding entries. The Leader Completeness "
        "property guarantees that if a log entry is committed in a given term, that entry will be present in the logs "
        "of the leaders for all higher terms."
    )
    for line in [p9[i:i+85] for i in range(0, len(p9), 85)]:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica", 9)
    c.drawString(width / 2 - 40, 36, "CourseWise AI Reference Document - Page 3")
    c.showPage()
    
    # PAGE 4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, height - 60, "4. Byzantine Fault Tolerance (BFT) and Practical Applications")
    c.line(54, height - 70, width - 54, height - 70)
    
    c.setFont("Helvetica", 10)
    y = height - 95
    p10 = (
        "A Byzantine fault refers to an arbitrary or adversarial failure where nodes can send conflicting messages, "
        "forge identities, or intentionally collude against system safety. The classic Byzantine Generals Problem "
        "established that in synchronous networks, reaching consensus requires strictly more than 3m + 1 total nodes "
        "to tolerate m Byzantine traitors."
    )
    for line in [p10[i:i+85] for i in range(0, len(p10), 85)]:
        c.drawString(54, y, line)
        y -= 14
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "4.1 Practical Byzantine Fault Tolerance (PBFT)")
    y -= 30
    p11 = (
        "Castro and Liskov (1999) introduced PBFT, the first practical algorithm achieving state machine replication "
        "under Byzantine conditions in asynchronous networks with polynomial time complexity O(R^2). PBFT processes "
        "requests through a three-phase commit pipeline: Pre-Prepare, Prepare, and Commit, relying on cryptographic "
        "digest signatures to guarantee non-repudiation."
    )
    for line in [p11[i:i+85] for i in range(0, len(p11), 85)]:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 10, "4.2 Comparative Summary of Consensus Protocols")
    y -= 30
    p12 = (
        "In production systems, Paxos and Raft are standard for crash-fault-tolerant (CFT) enterprise storage like "
        "etcd, Consul, Apache Kafka, and CockroachDB, operating with 2f + 1 nodes. For untrusted, adversarial "
        "environments, BFT protocols like PBFT, Tendermint, and HotStuff ensure safety with 3f + 1 nodes."
    )
    for line in [p12[i:i+85] for i in range(0, len(p12), 85)]:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica", 9)
    c.drawString(width / 2 - 40, 36, "CourseWise AI Reference Document - Page 4")
    c.showPage()
    
    c.save()
    print(f"Sample PDF created at: {output_path}")

if __name__ == "__main__":
    create_sample_course_pdf()
