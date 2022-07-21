use gtk::prelude::{GtkWindowExt,WidgetExt,WidgetExtManual};

/* Rubberband data for composited environment */
typedef struct
{
  gboolean left_pressed;
  gboolean rubber_banding;
  gboolean cancelled;
  gboolean move_rectangle;
  gint anchor;
  gint x;
  gint y;
  gint x_root;
  gint y_root;
  cairo_rectangle_int_t rectangle;
  GtkWidget *size_window;
  GtkWidget *size_label;
} RubberBandData;

fn cb_key_pressed(event &gdk::EventKey)
{
    let key = event.keyval();

    if key == gdk::keys::constants::Escape {
    }
}

fn get_rectangle_screenshot_composited()
{
    let window = gtk::Dialog::new();
    window.set_decorated(false);
    window.set_deletable(false);
    window.set_resizable(false);
    window.set_app_paintable(true);
    window.add_events(
        gdk::EventMask::BUTTON_RELEASE_MASK |
        gdk::EventMask::BUTTON_PRESS_MASK |
        gdk::EventMask::EXPOSURE_MASK |
        gdk::EventMask::POINTER_MOTION_MASK |
        gdk::EventMask::KEY_PRESS_MASK
    );

    // gtk_widget_set_visual (window, gdk_screen_get_rgba_visual (gdk_screen_get_default ()));
    //   gdk::Screen::default().unwrap();

    /* Connect to the interesting signals */
    window.connect_key_press_event();
}

fn main()
{
    get_rectangle_screenshot_composited();
}
