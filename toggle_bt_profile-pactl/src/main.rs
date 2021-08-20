use std::process;
use std::io;
use std::io::BufRead;


fn set_profile(card_name: &str, profile: &str)
{
    process::Command::new("pactl")
        .args(["set-card-profile", card_name, profile])
        .spawn()
        .unwrap();
}


fn main()
{
    let target_name = "bluez_card.94_DB_56_88_E9_8F";
    let headset_profile = "headset-head-unit";
    let audio_profile = "a2dp-sink";

    // each section is only about one card
    let card_re = regex::Regex::new(r"^Card #(\d+)").unwrap();
    // parse out the device name and active profile for each card
    let name_re_str = r#"^\s*device\.name = "([^\n]+)""#;
    let name_re = regex::Regex::new(name_re_str).unwrap();
    let active_profile_re_str = r"^\s*Active Profile: ([^\n]+)";
    let active_profile_re = regex::Regex::new(active_profile_re_str).unwrap();

    let child = process::Command::new("pactl")
        .args(["list", "cards"])
        .stdout(process::Stdio::piped())
        .spawn()
        .unwrap();
    let reader = io::BufReader::new(child.stdout.unwrap());

    let mut name = String::new();
    let mut active_profile = String::new();

    for line_r in reader.lines() {
        let line = line_r.unwrap();

        if name == target_name && active_profile != "" {
            let target_profile;
            if active_profile.starts_with(audio_profile) {
                target_profile = headset_profile;
            } else {
                target_profile = audio_profile;
            }
            set_profile(target_name, target_profile);
            break;
        }

        if let Some(_) = card_re.captures(line.as_str()) {
            name = String::new();
            active_profile = String::new();
            continue
        }

        if let Some(c) = name_re.captures(line.as_str()) {
            name = c.get(1).unwrap().as_str().to_string();
            continue
        }

        if let Some(c) = active_profile_re.captures(line.as_str()) {
            active_profile = c.get(1).unwrap().as_str().to_string();
            continue
        }

    }
}
