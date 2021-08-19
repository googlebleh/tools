#![allow(dead_code)]
#![allow(unused_variables)]

use std::process;
use std::io;
use std::io::BufRead;


fn set_profile(card_name: &str, profile: &str)
{
    let cmd = ["set-card-profile", card_name, profile];
    process::Command::new("pactl").args(&cmd);
}


fn main()
{
    let target_name = "bluez_card.94_DB_56_88_E9_8F";
    let target_headset_profile = "headset_head_unit";
    let target_audio_profile = "a2dp_sink";

    let child = process::Command::new("pactl")
        .args(["list", "cards"])
        .stdout(process::Stdio::piped())
        .spawn()
        .unwrap();

    let reader = io::BufReader::new(child.stdout.unwrap());

    let mut name: &str = "";
    let name_re = regex::Regex::new(r"\s*name: <([^<>\n]+?)>").unwrap();

    for line_r in reader.lines() {
        let line = line_r.unwrap();
        println!("{}", line);

        // if name == target_name and active_profile != "" {
        //     if active_profile
        // }

        name = match name_re.find(line.as_str()) {
            Some(m) => m.as_str(),
            _ => name,
        }
    }

    // loop {
    //
    //     match reader.read_line(&mut line) {
    //         Ok(0) => return,
    //         Ok(_) => (),
    //         _ => return,
    //     }
    //
    //     println!("{}", line);
    //
    //     // if name == target_name and active_profile != "" {
    //     //     if active_profile
    //     // }
    //
    //     name = match name_re.find(&line) {
    //         Some(m) => m.as_str(),
    //         _ => name,
    //     }
    //
    // }

}
