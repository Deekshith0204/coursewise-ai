import os
from pathlib import Path
import docx
from pptx import Presentation
from pptx.util import Inches, Pt

DATA_DIR = Path(__file__).resolve().parent


def create_sample_docx():
    path = DATA_DIR / "sample_cloud_edge.docx"
    doc = docx.Document()
    
    # Title
    doc.add_heading("Cloud and Edge Computing Architecture", level=0)
    
    # Section 1
    doc.add_heading("1. Introduction to Edge Computing", level=1)
    doc.add_paragraph(
        "Edge computing refers to a distributed computing paradigm that brings computation and data storage "
        "closer to the sources of data. This contrasts with traditional cloud paradigms where processing occurs "
        "in centralized data centers. Key advantages include bandwidth optimization, low latency response times, "
        "and offline autonomy for critical operational technology."
    )
    
    # Section 2
    doc.add_heading("2. Architectural Comparison: Edge vs Cloud", level=1)
    doc.add_paragraph("The architectural trade-offs between Edge and centralized Cloud systems are summarized below:")
    
    # Table
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Attribute"
    hdr_cells[1].text = "Edge Computing"
    hdr_cells[2].text = "Centralized Cloud"
    
    data = [
        ("Latency", "Sub-millisecond (1-10ms)", "High / Variable (50-200ms)"),
        ("Bandwidth Consumption", "Low (Local filtering)", "High (Raw stream transmission)"),
        ("Compute Capacity", "Constrained / Heterogeneous", "Virtually Unlimited Scalability"),
        ("Security Surface", "Decentralized endpoints", "Hardened central perimeter")
    ]
    for attr, edge_val, cloud_val in data:
        row_cells = table.add_row().cells
        row_cells[0].text = attr
        row_cells[1].text = edge_val
        row_cells[2].text = cloud_val

    # Section 3
    doc.add_heading("3. Implementation Considerations", level=1)
    doc.add_paragraph(
        "Deploying edge workloads requires container orchestration frameworks such as K3s or MicroK8s. "
        "Prerequisites include foundational understanding of computer networking, Linux process isolation, "
        "and distributed state synchronization."
    )
    
    doc.save(str(path))
    print(f"Created sample DOCX: {path}")


def create_sample_pptx():
    path = DATA_DIR / "sample_deep_learning.pptx"
    prs = Presentation()
    
    # Slide 1: Title Slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Deep Learning & Neural Network Foundations"
    slide.placeholders[1].text = "Lecture Series: Machine Learning Architecture\nDepartment of AI Studies"
    
    # Slide 2: Feedforward Networks
    bullet_layout = prs.slide_layouts[1]
    slide2 = prs.slides.add_slide(bullet_layout)
    slide2.shapes.title.text = "Feedforward Neural Networks (FNN)"
    tf2 = slide2.shapes.placeholders[1].text_frame
    tf2.text = "Multi-Layer Perceptron (MLP) Architecture"
    p = tf2.add_paragraph()
    p.text = "Composed of input, hidden, and output dense layers with nonlinear activations."
    p = tf2.add_paragraph()
    p.text = "Activation functions introduce non-linearity (ReLU, GELU, Sigmoid)."
    p = tf2.add_paragraph()
    p.text = "Objective: Minimize loss function via Backpropagation and Gradient Descent."
    
    # Notes for Slide 2
    notes_slide2 = slide2.notes_slide
    notes_slide2.notes_text_frame.text = "Emphasize why activation functions must be non-linear; linear activations collapse into a single layer."

    # Slide 3: Convolutional Neural Networks
    slide3 = prs.slides.add_slide(bullet_layout)
    slide3.shapes.title.text = "Convolutional Neural Networks (CNN)"
    tf3 = slide3.shapes.placeholders[1].text_frame
    tf3.text = "Spatial Invariance and Feature Extraction"
    p = tf3.add_paragraph()
    p.text = "Convolution operation: Kernel filters slide across 2D/3D tensor matrices."
    p = tf3.add_paragraph()
    p.text = "Pooling layers (MaxPooling) reduce spatial dimensionality and parameter count."
    p = tf3.add_paragraph()
    p.text = "Foundational Prerequisites: Matrix multiplication, linear algebra, digital image representations."

    # Slide 4: Optimization Protocols
    slide4 = prs.slides.add_slide(bullet_layout)
    slide4.shapes.title.text = "Stochastic Optimization: Adam and SGD"
    tf4 = slide4.shapes.placeholders[1].text_frame
    tf4.text = "Adaptive Learning Rate Algorithms"
    p = tf4.add_paragraph()
    p.text = "SGD with Momentum maintains an exponentially decaying moving average of past gradients."
    p = tf4.add_paragraph()
    p.text = "Adam computes adaptive learning rates for each parameter using first and second moment vectors."
    
    prs.save(str(path))
    print(f"Created sample PPTX: {path}")


def create_sample_txt():
    path = DATA_DIR / "sample_os_memory.txt"
    content = """CS402: Operating Systems - Virtual Memory Management
======================================================

1. Introduction to Virtual Memory
Virtual memory is defined as a memory management technique that provides an "idealized abstraction of the storage resources" that are actually available on a given machine. It creates the illusion to processes of a very large, uniform, contiguous address space.

Virtual addresses are translated to physical addresses by the Memory Management Unit (MMU) with hardware assistance.

2. Paging Mechanism and Page Tables
Paging divides virtual memory into fixed-size blocks called pages, and physical memory into blocks of the same size called page frames. Typical page size is 4KB (4096 bytes).

A Page Table maps virtual page numbers (VPN) to physical frame numbers (PFN).
When a virtual address is accessed that is not currently mapped into physical RAM, the MMU signals a Page Fault trap to the operating system kernel.

3. Page Replacement Algorithms
When a page fault occurs and no free physical frames exist, the OS must choose a victim page to evict to disk swap space:
- FIFO (First-In, First-Out): Simple queue, but suffers from Belady's Anomaly.
- LRU (Least Recently Used): Replaces the page that has not been accessed for the longest time.
- Clock (Second Chance): Approximation of LRU using a reference bit.

Prerequisites: Computer Architecture, cache hierarchies, interrupts, and pointer arithmetic.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Created sample TXT: {path}")


if __name__ == "__main__":
    create_sample_docx()
    create_sample_pptx()
    create_sample_txt()
