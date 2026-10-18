# Duplicate File Finder

A Python script that checks a folder for files with the same contents. The files can have different names and still show up as duplicates. It searches subfolders too.

It only prints the results. It doesn't delete or change anything.

## Running it

You'll need Python 3.9 or newer. No extra packages are needed.

Open a terminal in the project folder and try the included sample files:

```sh
python3 duplicate_finder.py sample_files
```

You should get this:

```text
Group 1: 2 matching files, 18 bytes each
  sample_files/notes/shopping-copy.txt
  sample_files/shopping.txt

Duplicate groups: 1
Extra content bytes: 18
Preview only. No files were changed.
```

To check your own folder, replace `sample_files` with its path:

```sh
python3 duplicate_finder.py "/path/to/my folder"
```

Use quotes if the path has spaces. On Windows, you might need to use `py` instead of `python3`.

## How it works

The script groups files by size first. Files with different sizes can't be identical, so there's no need to read all of them.

For files that could match, it calculates a SHA-256 hash. This is a fingerprint based on the file's contents. Files with the same size and hash are listed together.

Files are read in small chunks instead of loading the whole file into memory. The script uses `pathlib` for paths, `os.walk` to search folders, and `hashlib` for hashing.

## Project notes

Difficulty: medium. This project is practice with reading files, using dictionaries to group data, and accepting arguments from the terminal. Comments in the Python file explain the main steps.

A few things to keep in mind:

- Symbolic links are skipped so the scan doesn't follow links back into the same folders.
- Hidden files are included.
- If a file or folder can't be read, the script prints a warning and returns exit status 1. An invalid folder argument returns status 2.
- Avoid editing files while the scan is running. It checks the files as they are read, rather than taking a snapshot.
- Matching hashes are used to identify duplicates. There isn't a final byte-by-byte check.
- “Extra content bytes” adds up the copies beyond the first file in each group. Actual disk space savings could be different, especially with hard links or compression.
- Hard links count as separate file paths. Large folders can take a while to scan, and the list of paths is kept in memory.

## Tests

Run:

```sh
python3 -m unittest discover -s tests -v
```

There are five tests covering matching files in subfolders, different contents with the same size, empty files and folders, symbolic links, and read errors. They use temporary folders, so they don't touch your own files.

## Possible improvements

- Save the results to a CSV file.
- Show progress during longer scans.
- Add an option to ignore small files.
- Compare matching files byte by byte to confirm the results.

## Putting it on GitHub

Create an empty GitHub repository called `duplicate-file-finder`. Then run these commands from this folder:

```sh
git init -b main
git add .
git commit -m "Add duplicate file finder"
git remote add origin https://github.com/YOUR-USERNAME/duplicate-file-finder.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git asks for a name and email, set the identity you want attached to your commits.
