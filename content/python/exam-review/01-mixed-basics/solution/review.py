def normalise_name(raw):
    return " ".join(raw.split()).title()


def fizz_report(n):
    report = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            report.append("FizzBuzz")
        elif i % 3 == 0:
            report.append("Fizz")
        elif i % 5 == 0:
            report.append("Buzz")
        else:
            report.append(str(i))
    return report


def initials(full_name):
    return "".join(f"{word[0].upper()}." for word in full_name.split())


def bmi_category(weight, height):
    bmi = weight / height**2
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"
