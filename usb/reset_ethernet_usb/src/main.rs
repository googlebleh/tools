fn main() -> anyhow::Result<()>
{
    let dmesg = std::process::Command::new("dmesg")
        .output()?;

    let pci_re = regex_lite::Regex::new(concat!(
            r"\[\s*\d+\.\d+\] xhci_hcd (\d{4}:\d\d:\d\d\.\d): xHC error in resume, USBSTS 0x[0-9a-fA-F]+, Reinit\n",
            r"\[\s*\d+\.\d+\] usb usb\d: root hub lost power or was reset"
    ))?;

    let dmesg_str = std::str::from_utf8(&dmesg.stdout)?;
    if let Some(c) = pci_re.captures(dmesg_str) {
        let pci_address = c.get(1).unwrap().as_str();

        println!("rebinding xHCI device {} in bad state", pci_address);
        std::fs::write("/sys/bus/pci/drivers/xhci_hcd/unbind", pci_address)?;
        std::fs::write("/sys/bus/pci/drivers/xhci_hcd/bind", pci_address)?;
    } else {
        println!("couldn't find wedged xHCI device via dmesg");
    }

    return Ok(());
}
