use conversions::*;

#[test]
fn port_try_from() {
    assert_eq!(Port::try_from(8080u16), Ok(Port(8080)));
    assert_eq!(Port::try_from(0u16), Err(PortError::Zero));
    let p: Result<Port, _> = 443u16.try_into();
    assert_eq!(p, Ok(Port(443)));
}

#[test]
fn rgb_parse() {
    assert_eq!("rgb(255, 128, 0)".parse::<Rgb>(), Ok(Rgb { r: 255, g: 128, b: 0 }));
    assert_eq!("rgb(1,2,3)".parse::<Rgb>(), Ok(Rgb { r: 1, g: 2, b: 3 }));
}

#[test]
fn rgb_parse_errors() {
    for bad in ["rgb(256, 0, 0)", "rgb(1, 2)", "rgb(1, 2, 3, 4)", "(1, 2, 3)", "rgb(1, 2, 3", "rgb(a, b, c)", ""] {
        assert_eq!(bad.parse::<Rgb>(), Err(ParseRgbError), "{bad:?}");
    }
}

#[test]
fn rgb_into_string() {
    let s: String = Rgb { r: 255, g: 128, b: 0 }.into();
    assert_eq!(s, "#ff8000");
    assert_eq!(String::from(Rgb { r: 0, g: 10, b: 171 }), "#000aab");
}

#[test]
fn temperature_round_trip() {
    let f: Fahrenheit = Celsius(100.0).into();
    assert_eq!(f, Fahrenheit(212.0));
    let c: Celsius = Fahrenheit(-40.0).into();
    assert_eq!(c, Celsius(-40.0));
}

#[test]
fn as_ref_accepts_many_string_types() {
    let owned = vec![String::from("ab"), String::from("cde")];
    let borrowed = ["x", "yz"];
    assert_eq!(total_len(&owned), 5);
    assert_eq!(total_len(&borrowed), 3);
    let empty: [&str; 0] = [];
    assert_eq!(total_len(&empty), 0);
}

#[test]
fn non_empty_vec() {
    assert!(NonEmptyVec::<i32>::new(vec![]).is_none());
    let v = NonEmptyVec::new(vec![3, 1, 2]).unwrap();
    let first: &i32 = v.first();
    assert_eq!(*first, 3);
    assert_eq!(v.len(), 3);
    assert_eq!(v.iter().max(), Some(&3));
    assert!(v.contains(&2));
}
