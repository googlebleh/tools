use std::os::unix::fs::MetadataExt;

use clap::Parser;

/// Tools to check hard links. For now, just prints whether the files
/// are hard links of each other.
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// First path
    path_a: String,

    /// Second path
    path_b: String,
}

fn fpaths_are_linked(a: &std::fs::Metadata, b: &std::fs::Metadata) -> bool
{
    let inode_a = a.ino();
    let inode_b = b.ino();

    return inode_a == inode_b;
}

fn find_hardlink_to(dpath: String, file_meta: &std::fs::Metadata) -> anyhow::Result<Vec<String>>
{
    let mut found_paths = Vec::new();
    for de in walkdir::WalkDir::new(dpath) {
        let de = de?;
        let path = de.path();
        if path.is_file() {
            let meta_in_b = de.metadata()?;
            if fpaths_are_linked(&file_meta, &meta_in_b) {
                if let Some(path_str) = path.to_str() {
                    found_paths.push(path_str.to_owned());
                }
            }
        }
    }
    return Ok(found_paths);
}

fn main() -> anyhow::Result<()>
{
    let args = Args::parse();

    let meta_a = std::fs::metadata(&args.path_a)?;
    let meta_b = std::fs::metadata(&args.path_b)?;

    if meta_a.is_file() && meta_b.is_file() {
        if fpaths_are_linked(&meta_a, &meta_b) {
            println!("File paths are hard links of each other");
        } else {
            println!("File paths do not point to the same inode");
        }

    } else if meta_a.is_file() && meta_b.is_dir() {
        println!("looking for link of file a in dir b");
        for fpath in find_hardlink_to(args.path_b, &meta_a)? {
            println!("found hard link: {:?}", fpath);
        }

    } else if meta_a.is_dir() && meta_b.is_file() {
        println!("looking for link of file b in dir a");
        for fpath in find_hardlink_to(args.path_a, &meta_b)? {
            println!("found hard link: {:?}", fpath);
        }
    }

    return Ok(());
}
