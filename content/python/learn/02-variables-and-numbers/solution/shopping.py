apple_price = 0.45
apple_count = 12
bread_price = 2.35
bread_count = 2

apples_total = apple_price * apple_count
bread_total = bread_price * bread_count
total = round(apples_total + bread_total, 2)

paid = 20.0
change = round(paid - total, 2)

eggs = 40
boxes = eggs // 6
loose_eggs = eggs % 6
