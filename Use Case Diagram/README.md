# Mô tả hệ thống quản lý KTX
## I. Giới thiệu tổng quan
Hệ thống Quản lý Ký túc xá được thiết kế để giúp quản lý hiệu quả thông tin sinh viên, phòng ở, nhân viên và hóa đơn thanh toán trong ký túc xá. Hệ thống cung cấp các chức năng cơ bản như:
* Quản lý sinh viên (thêm, sửa, xóa, tra cứu).
* Quản lý phòng ở (đăng ký phòng, cập nhật cơ sở vật chất, kiểm tra phòng trống).
* Quản lý nhân viên (phân quyền, quản lý thông tin).
* Quản lý hóa đơn (tạo, in, tra cứu hóa đơn tiền phòng).
Hệ thống hướng tới đối tượng sử dụng gồm:
* Sinh viên: Tra cứu phòng, xem hóa đơn.
* Nhân viên quản lý KTX: Thao tác với dữ liệu sinh viên, phòng ở, hóa đơn.
* Quản trị viên: Toàn quyền quản lý hệ thống, bao gồm cả nhân viên.

## II. Yêu cầu chức năng 
### 1. Chức năng đăng nhập
* Thông tin đăng nhập: Tên đăng nhập, mật khẩu, email
* Người dùng quên mật khẩu sẽ được cấp lại qua email
### 2. Chức năng quản lý sinh viên:
* Thông tin sinh viên: Mã sinh viên, họ tên, ngày tháng năm sinh, quê quán, niên khóa, số điện thoại, …
* Thêm thông tin khi có sinh viên mới, thay đổi thông tin sinh viên.
### 3. Chức năng quản lý phòng:
* Thông tin phòng: Mã phòng, mô tả cơ sở vật chất có trong phòng (nóng lạnh, điều hòa, quạt, giường, bàn, tủ, …) số lượng phòng còn trống.
* Thêm mới phòng trống, sửa phòng, cập nhật số người ở
###4. Chức năng quản lý nhân viên:
* Thông tin nhân viên: Họ tên, giới tính, ngày tháng năm sinh, số điện thoại, quê quán, chức vụ, phòng ban.
* Thêm, sửa, xóa thông tin nhân viên.
### 5. Chức năng quản lý hóa đơn:
* Thông tin hóa đơn: Loại hóa đơn, chủ sở hữu hóa đơn.
* Tra cứu, thêm, xóa thông tin hóa đơn.

## III. Yêu cầu phi chức năng
* Hệ thống hoạt động ổn định, dễ sử dụng, khả năng truy cập dữ liệu nhanh chóng và chính xác.
* Giao diện người dùng thiết kế một cách khoa học, thân thiện với người sử dụng.
* Hệ thống đáp ứng được nhu cầu tìm kiếm đa dạng, cho biết về thông tin sinh viên bất kỳ nhanh chóng, dễ dàng, và chính xác.
* Hệ thống có các biện pháp bảo mật để bảo vệ thông tin cá nhân.
* Hệ thống hỗ trợ đa nền tảng để có thể sử dụng trên các thiết bị khác nhau.
