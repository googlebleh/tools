fn set_gtk_notification_location(corner: gtk_sys::GtkCornerType) -> Result<(), std::io::Error>
{
    std::process::Command::new("xfconf-query")
        .args([
            "-c", "xfce4-notifyd",
            "-p", "/notify-location",
            "-s", &corner.to_string(),
        ])
        .status()
        .unwrap();
    return Ok(());
}


fn main() -> Result<(), std::io::Error>
{
    // let monitors = xrandr::XHandle::open().unwrap()
    //     .monitors().unwrap();
    // for m in monitors {
    //     println!("{:#?}", m);
    // }

    println!("{}", gtk_sys::GTK_CORNER_TOP_LEFT);
    println!("{}", gtk_sys::GTK_CORNER_TOP_RIGHT);

    let using_huge_monitor_only = std::path::Path::new("/tmp/is_big_monitor").exists();

    // if using_huge_monitor_only {
    //     set_gtk_notification_location(gtk_sys::GTK_CORNER_TOP_LEFT)?;
    // } else {
    //     set_gtk_notification_location(gtk_sys::GTK_CORNER_TOP_RIGHT)?;
    // }

    return Ok(());
}
