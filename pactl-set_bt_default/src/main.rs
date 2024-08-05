use serde_json::value::Value;

#[derive(serde::Deserialize, PartialEq, Debug)]
struct PactlCard {
    name: String,
    active_profile: String,
}

#[derive(serde::Deserialize, PartialEq, Debug)]
struct PactlSink {
    name: String,
    properties: Value,
}


#[derive(serde::Deserialize, PartialEq, Debug)]
struct PactlSource {
    name: String,
    properties: Value,
}


fn notify_mic_on()
{
    std::process::Command::new("notify-send")
        .args([
            "--icon", "/usr/share/icons/ePapirus/32x32/devices/audio-input-microphone.svg",
            "Bluetooth Toggle",
            "Microphone/Headset Active",
        ])
        .spawn()
        .unwrap();
}


fn notify_a2dp()
{
    std::process::Command::new("notify-send")
        .args([
            "--icon", "/usr/share/icons/ePapirus/32x32/devices/audio-headphones.svg",
            "Bluetooth Toggle",
            "A2DP Active",
        ])
        .spawn()
        .unwrap();
}


fn pactl_sync()
{
    // Pipewire's pactl gets confused when running several commands in
    // succession. Wait about this long for each command to take effect
    // before issuing another.
    std::thread::sleep(std::time::Duration::from_millis(1250));
}


fn set_default_sink(target: &str)
{
    let pactl_list_sinks = std::process::Command::new("pactl")
        .args([
            "-f", "json",
            "list", "sinks",
        ])
        .output()
        .unwrap();

    let pactl_sinks: Vec<PactlSink> = serde_json::from_slice(&pactl_list_sinks.stdout)
        .unwrap();
    for sink in &pactl_sinks {
        if sink.properties["device.name"] == target {
            std::process::Command::new("pactl")
                .args(["set-default-sink", &sink.name])
                .spawn()
                .unwrap();

            pactl_sync();
            break;
        }
    }
}

fn set_default_source(target: &str)
{
    let pactl_list_sources = std::process::Command::new("pactl")
        .args([
            "-f", "json",
            "list", "sources",
        ])
        .output()
        .unwrap();

    let pactl_sources: Vec<PactlSource> = serde_json::from_slice(&pactl_list_sources.stdout)
        .unwrap();
    for source in &pactl_sources {
        if source.properties["device.name"] == target
            && source.properties["media.class"] == "Audio/Source" {

            std::process::Command::new("pactl")
                .args(["set-default-source", &source.name])
                .spawn()
                .unwrap();

            pactl_sync();
            break;
        }
    }
}


fn main()
{
    let target_names = vec!(
        "bluez_card.94_DB_56_88_E9_8F", // WF-1000XM4 headphones
        "bluez_card.88_C9_E8_2E_85_B4", // WF-1000XM4 earbuds
        "bluez_card.AC_80_0A_C3_F7_9C", // WF-1000XM5 earbuds
    );
    let headset_profile = "headset-head-unit";
    let audio_profile = "a2dp-sink";

    let pactl_list_cards = std::process::Command::new("pactl")
        .args([
            "-f", "json",
            "list", "cards",
        ])
        .output()
        .unwrap();

    let pactl_cards: Vec<PactlCard> = serde_json::from_slice(&pactl_list_cards.stdout)
        .unwrap();
    for card in &pactl_cards {
        if target_names.contains(&card.name.as_str()) && card.active_profile != "off" {
            if card.active_profile.starts_with(audio_profile) {
                notify_a2dp();
                set_default_sink(&card.name);

            } else if card.active_profile.starts_with(headset_profile) {
                notify_mic_on();
                set_default_source(&card.name);
                set_default_sink(&card.name);
            }
        }
    }
}
