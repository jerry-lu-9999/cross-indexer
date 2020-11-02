mod fib;
use fib::fib;
use std::env;

fn main() {
    for argument in env::args() {
        let number: i32 = match argument.parse() {
            Ok(n) => n,
            Err(_) => continue,
        };
        println!("{}", fib(number));
    }
}