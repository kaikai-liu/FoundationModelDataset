from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = Path(__file__).resolve().parent.parent
PREV = ROOT / 'datasets' / 'seisdare' / 'sotiel' / 'outputs'
OUT = ROOT / 'datasets' / 'seisdare' / 'sotiel' / 'outputs' / 'SeisDARE Summary Slide.png'

img1 = mpimg.imread(PREV / 'geometry_file_layout.png')
img2 = mpimg.imread(PREV / 'geometry_vs_trace_overlay.png')
img3 = mpimg.imread(PREV / 'field_record_1076_layout.png')

fig = plt.figure(figsize=(16, 9), dpi=180)
fig.patch.set_facecolor('white')

# Title area
ax_title = fig.add_axes([0.04, 0.87, 0.92, 0.11])
ax_title.axis('off')
ax_title.text(0.0, 0.72, 'SeisDARE / Sotiel-Elvira — Geometry + Trace Layout Summary', fontsize=24, fontweight='bold', ha='left', va='center')
ax_title.text(0.0, 0.20, 'Local inspection of the smaller SEG-Y file confirms the dataset is spatially grounded, internally consistent, and usable for seismic ML prototyping.', fontsize=13, ha='left', va='center')

# Left text block
ax_text = fig.add_axes([0.04, 0.08, 0.29, 0.76])
ax_text.axis('off')
text = (
    'Key findings\n'
    '• Geometry file contains 1,563 survey points\n'
    '• 910 coded positions and 653 uncoded positions\n'
    '• SEG-Y file contains 30,038 traces\n'
    '• 46 unique shot locations in this smaller file\n'
    '• 644 unique receiver coordinates\n'
    '• The file behaves like a coherent survey subset\n'
    '\n'
    'Why it matters\n'
    '• Trace headers can be linked back to physical layout\n'
    '• Good fit for geometry-aware preprocessing\n'
    '• Good fit for shot-gather visualization\n'
    '• Good fit for spatially informed seismic encoders\n'
    '\n'
    'Bottom line\n'
    'This is a real, usable mining seismic dataset.\n'
    'It is much more relevant than the DAS event dataset\n'
    'for subsurface mining detection work.'
)
ax_text.text(0.0, 1.0, text, fontsize=15, ha='left', va='top', linespacing=1.5)

# Images
axes = [
    fig.add_axes([0.37, 0.50, 0.27, 0.31]),
    fig.add_axes([0.67, 0.50, 0.29, 0.31]),
    fig.add_axes([0.52, 0.10, 0.34, 0.29]),
]
for ax, img, title in zip(
    axes,
    [img1, img2, img3],
    ['Geometry file layout', 'Geometry vs trace-header overlay', 'Single shot-gather footprint'],
):
    ax.imshow(img)
    ax.set_title(title, fontsize=13)
    ax.axis('off')

plt.savefig(OUT, bbox_inches='tight')
print(f'Saved {OUT}')
