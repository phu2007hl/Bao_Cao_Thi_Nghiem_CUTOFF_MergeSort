# Dữ liệu thí nghiệm

Thư mục `data/generated/` chứa 13 tệp dữ liệu đầu vào được dùng trong benchmark CUTOFF cho MergeSort. Mỗi dòng của tệp là một số nguyên và không có dòng tiêu đề.

## Danh sách dataset

| Tên | Kích thước | Ý nghĩa |
|---|---:|---|
| `random_10000.txt` đến `random_1000000.txt` | 10.000 đến 1.000.000 | Số nguyên giả ngẫu nhiên trong miền 0 đến 1.000.000.000. |
| `sorted_100000.txt` | 100.000 | Mảng tăng dần. |
| `reversed_100000.txt` | 100.000 | Mảng giảm dần. |
| `nearly_sorted_100000.txt` | 100.000 | Mảng tăng dần sau khi hoán đổi khoảng 1% vị trí. |
| `few_distinct_100000.txt` | 100.000 | Các phần tử chỉ nhận một trong 10 giá trị. |
| `all_equal_100000.txt` | 100.000 | Tất cả phần tử bằng 0. |
| `edge_values_10000.txt` | 10.000 | Dữ liệu random có bổ sung `Integer.MIN_VALUE`, -1, 0 và `Integer.MAX_VALUE`. |

## Tái tạo dữ liệu

Dữ liệu được sinh bằng `InputGenerator` với seed mặc định `20261116`:

```powershell
New-Item -ItemType Directory -Force build
javac -d build (Get-ChildItem -Recurse src -Filter *.java | ForEach-Object FullName)
java -cp build Main generate data/generated 20261116
```

Seed cần được giữ nguyên nếu muốn tái lập đúng các kết quả CSV hiện có. Nếu thay seed, dữ liệu thay đổi và cần chạy lại toàn bộ benchmark trước khi so sánh.

## Liên hệ với kết quả

Tên dataset được dùng thống nhất trong tên các file:

- `data/generated/random_100000.txt` tương ứng với `results/raw/random_100000.csv` và `results/raw/runs_random_100000.csv`.
- Các batch lặp lại dùng cùng dữ liệu trong `results/repeated/batch_1` đến `batch_5`.
- Các bảng tổng hợp nằm ở `results/summary/` và `results/repeated/summary/`.
