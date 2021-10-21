use std::process;
use std::io;
use std::io::BufRead;
use std::thread;
use std::time;


fn pactl_sync()
{
    // Pipewire's pactl gets confused when running several commands in
    // succession. Wait about this long for each command to take effect
    // before issuing another.
    thread::sleep(time::Duration::from_millis(1250));
}


fn set_profile(card_name: &str, profile: &str)
{
    process::Command::new("pactl")
        .args(["set-card-profile", card_name, profile])
        .spawn()
        .unwrap();

    pactl_sync();
}


fn set_default_sink()
{
    // make sure card is set as default sink
    let child = process::Command::new("pactl")
        .args(["list", "sinks"])
        .stdout(process::Stdio::piped())
        .spawn()
        .unwrap();
    let reader = io::BufReader::new(child.stdout.unwrap());

    let sink_re = regex::Regex::new(r"^Sink #\d+").unwrap();
    let name_re_str = r"^\s+Name: (bluez_output\.94_DB_56_88_E9_8F\..+)";
    let name_re = regex::Regex::new(name_re_str).unwrap();

    let mut sink_name = String::new();

    for line_r in reader.lines() {
        let line = line_r.unwrap();

        if sink_re.is_match(line.as_str()) {
            sink_name = "".to_string();
            continue
        }

        if let Some(c) = name_re.captures(line.as_str()) {
            sink_name = c.get(1).unwrap().as_str().to_string();
            println!("set sink name {}", sink_name);
            break;
        }

    }

    process::Command::new("pactl")
        .args(["set-default-sink", &sink_name])
        .spawn()
        .unwrap();

    pactl_sync();
}


fn set_default_source()
{
    // make sure card is set as default source
    let child = process::Command::new("pactl")
        .args(["list", "sources"])
        .stdout(process::Stdio::piped())
        .spawn()
        .unwrap();
    let reader = io::BufReader::new(child.stdout.unwrap());

    let source_re = regex::Regex::new(r"^Source #\d+").unwrap();
    let name_re_str = r"^\s+Name: (bluez_input\.94_DB_56_88_E9_8F\..+)";
    let name_re = regex::Regex::new(name_re_str).unwrap();

    let mut source_name = String::new();

    for line_r in reader.lines() {
        let line = line_r.unwrap();

        if source_re.is_match(line.as_str()) {
            source_name = "".to_string();
            continue
        }

        if let Some(c) = name_re.captures(line.as_str()) {
            source_name = c.get(1).unwrap().as_str().to_string();
            println!("set source name {}", source_name);
            break;
        }

    }

    process::Command::new("pactl")
        .args(["set-default-source", &source_name])
        .spawn()
        .unwrap();

    pactl_sync();
}


fn set_current_mic_vol(volume_percent: u8)
{
    let cmd = [
        "set-source-volume",
        "@DEFAULT_SOURCE@",
        &format!("{}%", volume_percent),
    ];
    process::Command::new("pactl")
        .args(cmd)
        .spawn()
        .unwrap();

    pactl_sync();
}


fn notify_mic_on()
{
    let cmd = [
        "--icon",
        "/usr/share/icons/ePapirus/32x32/devices/audio-input-microphone.svg",
        "WH-1000XM4 Toggle",
        "Microphone/Headset Active",
    ];
    process::Command::new("notify-send")
        .args(&cmd)
        .spawn()
        .unwrap();
}


fn notify_a2dp()
{
    let cmd = [
        "--icon",
        "/usr/share/icons/ePapirus/32x32/devices/audio-headphones.svg",
        "WH-1000XM4 Toggle",
        "A2DP Active",
    ];
    process::Command::new("notify-send")
        .args(&cmd)
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

        // matched current state
        if name == target_name && active_profile != "" {
            if active_profile.starts_with(audio_profile) {
                notify_a2dp();
                set_default_sink();
            } else if active_profile.starts_with(headset_profile) {
                notify_mic_on();
                set_default_source();
                set_default_sink();
            }
            break;
        }

        // determine current state

        if card_re.is_match(line.as_str()) {
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
