import os

def get_file_size_kb(path):
    """
    Return the size of a single file in kilobytes (KB), rounded to 2 decimal places.

    Parameters:
        path (str or Path): Path to the file.

    Returns:
        float: File size in kilobytes.

    Example:
        >>> get_file_size_kb("ENC_ROOT/V25AT001.000")
        231.42
    """
    return round(os.path.getsize(path) / 1024, 2)


def get_dir_size_kb(dir_path):
    """
    Recursively calculate the total size of a directory in kilobytes (KB),
    summing all files inside the directory and its subdirectories.

    Parameters:
        dir_path (str or Path): Path to the directory.

    Returns:
        float: Total size of all files in kilobytes.

    Example:
        >>> get_dir_size_kb("tiles/V25AT001")
        28512.17
    """
    total = 0
    for dirpath, _, filenames in os.walk(dir_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return round(total / 1024, 2)
