use std::env;

fn fib(n: i32) -> i32 {
    if n < 2 {
        n
    } else {
        fib(n - 2) + fib (n - 1)
    }
}

fn main() {
    for argument in env::args() {
        let number: i32 = match argument.parse() {
            Ok(n) => n,
            Err(_) => continue,
        };
        println!("{}", fib(number));
    }
}