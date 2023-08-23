// TODO: fix indenting
// TODO: improve logging
// TODO: dry-run mode
// TODO: re-structure to avoid many nested indents

/// Bard: "rust equivalent of multiplying a string by an integer in
/// python"
fn multiply_string_by_integer(string: &str, integer: i32) -> String
{
    let mut new_string = String::new();

    for _ in 0..integer {
        new_string.push_str(string);
    }

    return new_string;
}


fn rmdir_recursive(dpath: &str, depth: i32) -> anyhow::Result<()>
{
    for entry in std::fs::read_dir(dpath)? {
        let entry = entry?;
        let entry_type = entry.file_type()?;
        
        if entry_type.is_dir() {
            if let Some(subdir) = entry.path().to_str() {
                let indent = multiply_string_by_integer("    ", depth);
                println!("{}{}", indent, subdir);
                if let Err(e) = rmdir_recursive(subdir, depth + 1) {
                    return Err(e);
                }
            } else {
                return Err(anyhow::anyhow!("found non utf-8 path"));
            }
        }
    }
    return Ok(std::fs::remove_dir(dpath)?);
}


fn main() -> anyhow::Result<()>
{
    for arg in std::env::args().skip(1) {
        println!("{}", arg);
        if let Err(e) = rmdir_recursive(&arg, 0) {
            return Err(e);
        }
    }

    return Ok(());
}
