# Data Directory

This project uses the **NSL-KDD** network intrusion detection dataset.

## Files

| File | Description |
|------|-------------|
| `KDDTrain+.txt` | Official NSL-KDD training split (125,973 connection records) |
| `KDDTest+.txt` | Official NSL-KDD test split (22,544 connection records) |

## Download

The files are **not committed to Git** because of size. Download them before running the notebook:

```bash
python scripts/download_data.py
```

Or manually from:

- Official source: https://www.unb.ca/cic/datasets/nsl.html
- Mirror used in this project: https://github.com/jmnwong/NSL-KDD-Dataset

## Columns

Each row describes one TCP/UDP connection with 41 features plus:

- `label` — attack type or `normal`
- `difficulty` — difficulty score assigned in NSL-KDD

## License

Use the dataset according to the University of New Brunswick / Canadian Institute for Cybersecurity terms.
