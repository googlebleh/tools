use std::env;
use users::get_group_by_gid;

/**
 * usage:
 *  $ /tmp/gid_name $(sed -n 's/^Groups://p' /proc/$(pidof wine)/status)
 */

fn main()
{
    let argv: Vec<String> = env::args().collect();

    for arg in argv {
        let gid_r = arg.parse::<u32>();
        let gid = match gid_r {
            Err(_) => {
                println!("couldn't parse gid {}", arg);
                continue;
            },
            Ok(gid) => gid,
        };

        let gid_name_o = get_group_by_gid(gid);
        let gid_name = match gid_name_o {
            None => {
                println!("couldn't get group name for gid={}", gid);
                continue;
            },
            Some(gid_name) => gid_name,
        };

        println!("{} {:?}", gid, gid_name.name());
    }
}
