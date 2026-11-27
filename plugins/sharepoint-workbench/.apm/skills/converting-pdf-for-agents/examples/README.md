# Examples

- `sample-handbook.pdf`: 4-page text-layer PDF (headings, a numbered list, two ruled tables, running footer, a PNG chart with caption, a JPEG photo, a drawn chart with caption, a 32 px icon and a logo on every page). Default build extracts 3 pictures (2 files; the chart appears twice); `--vector-figures` adds the drawn chart.
- `sample-no-images.pdf`: same text and tables, no images.
- `make_sample_pdf.py`: regenerates both (needs reportlab and Pillow).

Try both formats:

```bash
python scripts/convert_pdf.py plan examples/sample-handbook.pdf --work working/demo/work
python scripts/convert_pdf.py build examples/sample-handbook.pdf --topics working/demo/work/topics.xlsx --out working/demo/agent-md --format agent-md
python scripts/convert_pdf.py build examples/sample-handbook.pdf --topics working/demo/work/topics.xlsx --out working/demo/html --format html
python scripts/selftest.py   # runs everything and checks the results
```
