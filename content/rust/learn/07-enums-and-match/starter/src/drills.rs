// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

/// A traffic light. Already written: read it first.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Light {
    Red,
    Yellow,
    Green,
}

/// A pet; two of the variants carry data.
#[derive(Debug, PartialEq)]
pub enum Pet {
    Dog(String),
    Cat { lives: u32 },
    Fish,
}

/// Drill 1: `next_light(Light::Red)` is `Light::Green`; green goes to yellow, yellow to red
pub fn next_light(light: Light) -> Light {
    todo!()
}

/// Drill 2: `seconds(&Light::Red)` is `30`; yellow `5`, green `25`
pub fn seconds(light: &Light) -> u32 {
    todo!()
}

/// Drill 3: `can_go(&Light::Green)` is `true`, anything else `false`
pub fn can_go(light: &Light) -> bool {
    todo!()
}

/// Drill 4: `size_word(0)` is `"none"`, 1 to 3 `"few"`, more `"many"`
pub fn size_word(n: u32) -> String {
    todo!()
}

/// Drill 5: `is_fish(&Pet::Fish)` is `true`
pub fn is_fish(pet: &Pet) -> bool {
    todo!()
}

/// Drill 6: `lives(&Pet::Cat { lives: 9 })` is `9`; any other pet `1`
pub fn lives(pet: &Pet) -> u32 {
    todo!()
}

/// Drill 7: `pet_text(&Pet::Dog("rex".into()))` is `"dog rex"`; a cat with 9 lives is `"cat with 9 lives"`; a fish is `"fish"`
pub fn pet_text(pet: &Pet) -> String {
    todo!()
}

/// Drill 8: `dog_name(&pet)` is the dog's name, or `""` for any other pet
pub fn dog_name(pet: &Pet) -> String {
    todo!()
}

/// Drill 9: `Light::Red.is_red()` is `true`
impl Light {
    pub fn is_red(&self) -> bool {
        todo!()
    }
}
