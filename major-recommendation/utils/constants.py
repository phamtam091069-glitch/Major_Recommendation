"""Tham so du an — dung chung cho train, predictor va Flask."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "students.csv"
MODELS_DIR = BASE_DIR / "models"
MAJORS_SOURCE_PATH = MODELS_DIR / "majors.json"
REPORTS_DIR = BASE_DIR / "reports"

CATEGORICAL_COLS = [
    "so_thich_chinh",
    "mon_hoc_yeu_thich",
    "ky_nang_noi_bat",
    "tinh_cach",
    "moi_truong_lam_viec_mong_muon",
    "muc_tieu_nghe_nghiep",
]
TEXT_COLS = ["mo_ta_ban_than", "dinh_huong_tuong_lai"]
TARGET_COL = "nganh_phu_hop"

# Dung cong thuc lai theo de cuong: 60% Random Forest + 40% Cosine
HYBRID_WEIGHT_RF = 0.6
HYBRID_WEIGHT_COSINE = 0.4

MODEL_RF_PATH = MODELS_DIR / "rf_model.pkl"
MODEL_OHE_PATH = MODELS_DIR / "ohe.pkl"
MODEL_TFIDF_PATH = MODELS_DIR / "tfidf.pkl"
MODEL_CLASSES_PATH = MODELS_DIR / "classes.pkl"
MODEL_MAJORS_PATH = MODELS_DIR / "majors.json"
HYBRID_CONFIG_PATH = MODELS_DIR / "hybrid_config.json"

MAJOR_DISPLAY = {
    "Cong nghe thong tin": "Công nghệ thông tin",
    "Ky thuat phan mem": "Kỹ thuật phần mềm",
    "Khoa hoc du lieu": "Khoa học dữ liệu",
    "Tri tue nhan tao": "Trí tuệ nhân tạo",
    "An ninh mang": "An ninh mạng",
    "He thong thong tin": "Hệ thống thông tin",
    "Ky thuat may tinh": "Kỹ thuật máy tính",
    "Ky thuat dien dien tu": "Kỹ thuật điện - điện tử",
    "Tu dong hoa": "Tự động hóa",
    "Ky thuat co khi": "Kỹ thuật cơ khí",
    "Ky thuat o to": "Kỹ thuật ô tô",
    "Ky thuat xay dung": "Kỹ thuật xây dựng",
    "Quan tri kinh doanh": "Quản trị kinh doanh",
    "Marketing": "Marketing",
    "Thuong mai dien tu": "Thương mại điện tử",
    "Tai chinh ngan hang": "Tài chính - Ngân hàng",
    "Ke toan": "Kế toán",
    "Kiem toan": "Kiểm toán",
    "Logistics va quan ly chuoi cung ung": "Logistics và quản lý chuỗi cung ứng",
    "Quan tri nhan luc": "Quản trị nhân lực",
    "Kinh doanh quoc te": "Kinh doanh quốc tế",
    "Quan tri khach san": "Quản trị khách sạn",
    "Quan tri nha hang va dich vu an uong": "Quản trị nhà hàng và dịch vụ ăn uống",
    "Khoi nghiep va doi moi sang tao": "Khởi nghiệp và đổi mới sáng tạo",
    "Ngon ngu Anh": "Ngôn ngữ Anh",
    "Ngon ngu Trung": "Ngôn ngữ Trung",
    "Ngon ngu Nhat": "Ngôn ngữ Nhật",
    "Ngon ngu Han": "Ngôn ngữ Hàn",
    "Bao chi": "Báo chí",
    "Truyen thong da phuong tien": "Truyền thông đa phương tiện",
    "Quan he cong chung": "Quan hệ công chúng",
    "Luat": "Luật",
    "Luat kinh te": "Luật kinh tế",
    "Tam ly hoc": "Tâm lý học",
    "Cong tac xa hoi": "Công tác xã hội",
    "Su pham Toan hoc": "Sư phạm Toán học",
    "Y da khoa": "Y đa khoa",
    "Duoc hoc": "Dược học",
    "Dieu duong": "Điều dưỡng",
    "Ky thuat xet nghiem y hoc": "Kỹ thuật xét nghiệm y học",
    "Ky thuat hinh anh y hoc": "Kỹ thuật hình ảnh y học",
    "Y hoc co truyen": "Y học cổ truyền",
    "Rang ham mat": "Răng - Hàm - Mặt",
    "Dinh duong": "Dinh dưỡng",
    "Y te cong cong": "Y tế công cộng",
    "Ho sinh": "Hộ sinh",
    "Vat ly tri lieu va phuc hoi chuc nang": "Vật lý trị liệu và phục hồi chức năng",
    "Quan ly benh vien": "Quản lý bệnh viện",
    "Thiet ke do hoa": "Thiết kế đồ họa",
    "Thiet ke thoi trang": "Thiết kế thời trang",
    "Thiet ke noi that": "Thiết kế nội thất",
    "Kien truc": "Kiến trúc",
    "My thuat": "Mỹ thuật",
    "Nhiếp anh": "Nhiếp ảnh",
    "Quay phim - Dung phim": "Quay phim - Dựng phim",
    "Du lich": "Du lịch",
    "Quan tri dich vu du lich va lu hanh": "Quản trị dịch vụ du lịch và lữ hành",
    "Huong dan du lich": "Hướng dẫn du lịch",
    "Thiet ke game": "Thiết kế game",
    "Nghe thuat so": "Nghệ thuật số",
    "Dieu khien va quan ly tau bien": "Điều khiển và quản lý tàu biển",
    "Khai thac may tau thuy va quan ly ky thuat": "Khai thác máy tàu thủy và quản lý kỹ thuật",
}

# Gợi ý cụ thể cho từng ngành
SUGGESTION_VI = {
    "Cong nghe thong tin": "Xây dựng dự án lập trình thực tế, tham gia hackathon, học thêm về cloud computing.",
    "Ky thuat phan mem": "Thực hành dự án web/mobile, học quy trình phát triển phần mềm, kiểm thử và Git.",
    "Khoa hoc du lieu": "Làm quen với Python, R, SQL. Tham gia các dự án phân tích dữ liệu thực tế.",
    "Tri tue nhan tao": "Học machine learning, deep learning, dữ liệu lớn và triển khai mô hình AI.",
    "An ninh mang": "Luyện kỹ năng bảo mật hệ thống, mạng máy tính, pentest và xử lý sự cố.",
    "He thong thong tin": "Học về ERP, quản lý cơ sở dữ liệu, và business process.",
    "Ky thuat may tinh": "Nắm chắc phần cứng, hệ điều hành, mạng và lập trình hệ thống.",
    "Ky thuat dien dien tu": "Làm quen mạch điện, cảm biến, điều khiển và điện tử công nghiệp.",
    "Tu dong hoa": "Tìm hiểu PLC, SCADA, robot, cảm biến và hệ thống điều khiển.",
    "Ky thuat co khi": "Tham gia các câu lạc bộ kỹ thuật, học CAD, 3D design.",
    "Ky thuat o to": "Thực hành chẩn đoán, bảo trì, hệ thống điện ô tô và công nghệ xe.",
    "Ky thuat xay dung": "Học AutoCAD, kết cấu, thi công và tham gia các dự án công trình.",
    "Quan tri kinh doanh": "Tìm hiểu về quản lý dự án, lãnh đạo đội nhóm, chiến lược kinh doanh.",
    "Marketing": "Học digital marketing, phân tích thị trường, sáng tạo nội dung và branding.",
    "Thuong mai dien tu": "Nghiên cứu vận hành sàn TMĐT, quảng cáo số và quản lý khách hàng.",
    "Tai chinh ngan hang": "Rèn luyện phân tích số liệu, đầu tư, tín dụng và quản trị rủi ro.",
    "Ke toan": "Nắm vững Excel, kế toán tài chính, thuế.",
    "Kiem toan": "Luyện phân tích báo cáo, kiểm tra số liệu và đánh giá rủi ro.",
    "Logistics va quan ly chuoi cung ung": "Hiểu về kho vận, phân phối, xuất nhập khẩu và tối ưu chi phí.",
    "Quan tri nhan luc": "Tìm hiểu tuyển dụng, đào tạo, chính sách nhân sự và văn hóa doanh nghiệp.",
    "Kinh doanh quoc te": "Rèn kỹ năng đàm phán, ngoại ngữ và thương mại quốc tế.",
    "Quan tri khach san": "Thực hành dịch vụ khách hàng, vận hành khách sạn và du lịch.",
    "Quan tri nha hang va dich vu an uong": "Làm quen quản lý vận hành, tiêu chuẩn phục vụ và an toàn thực phẩm.",
    "Khoi nghiep va doi moi sang tao": "Xây dựng ý tưởng sản phẩm, tư duy kinh doanh và phát triển mô hình.",
    "Ngon ngu Anh": "Nâng cao trình độ tiếng Anh qua sách, phim, podcast.",
    "Ngon ngu Trung": "Luyện nghe-nói-đọc-viết và tìm hiểu văn hóa, thương mại.",
    "Ngon ngu Nhat": "Rèn ngoại ngữ và văn hóa doanh nghiệp Nhật Bản.",
    "Ngon ngu Han": "Luyện giao tiếp, dịch thuật và văn hóa Hàn Quốc.",
    "Bao chi": "Viết bài, phỏng vấn, biên tập tin tức và kể chuyện báo chí.",
    "Truyen thong da phuong tien": "Phát triển content, video, social media và storytelling.",
    "Quan he cong chung": "Học PR, sự kiện, truyền thông thương hiệu và quan hệ đối tác.",
    "Luat": "Tìm hiểu pháp luật, lập luận, phân tích hồ sơ và kỹ năng tranh biện.",
    "Luat kinh te": "Nghiên cứu hợp đồng, thương mại, doanh nghiệp và tư vấn pháp lý.",
    "Tam ly hoc": "Rèn kỹ năng lắng nghe, tư vấn và thấu hiểu hành vi con người.",
    "Cong tac xa hoi": "Học hỗ trợ cộng đồng, tư vấn xã hội và làm việc với các nhóm yếu thế.",
    "Su pham Toan hoc": "Tìm hiểu phương pháp giảng dạy, sư phạm và truyền đạt kiến thức.",
    "Y da khoa": "Học giải phẫu, lâm sàng, chẩn đoán và chăm sóc người bệnh.",
    "Duoc hoc": "Nắm dược lý, kiểm soát chất lượng thuốc và tư vấn sử dụng thuốc.",
    "Dieu duong": "Thực tập tại bệnh viện, học kỹ năng chăm sóc và giao tiếp.",
    "Ky thuat xet nghiem y hoc": "Làm quen với mẫu xét nghiệm, sinh học và quy trình phòng lab.",
    "Ky thuat hinh anh y hoc": "Học chẩn đoán hình ảnh, X-quang, CT, MRI và an toàn y tế.",
    "Y hoc co truyen": "Tìm hiểu y học cổ truyền, châm cứu và dược liệu.",
    "Rang ham mat": "Rèn độ chính xác, kỹ năng lâm sàng và chăm sóc nha khoa.",
    "Dinh duong": "Nghiên cứu chế độ ăn, tư vấn sức khỏe và phân tích dinh dưỡng.",
    "Y te cong cong": "Tìm hiểu phòng bệnh, truyền thông sức khỏe và chính sách y tế.",
    "Ho sinh": "Học chăm sóc mẹ và bé, an toàn sinh nở và hỗ trợ lâm sàng.",
    "Vat ly tri lieu va phuc hoi chuc nang": "Thực hành phục hồi vận động và hỗ trợ bệnh nhân.",
    "Quan ly benh vien": "Tìm hiểu điều hành y tế, quy trình bệnh viện và quản lý dịch vụ.",
    "Thiet ke do hoa": "Nắm vững Figma, Adobe XD, UI/UX design principles.",
    "Thiet ke thoi trang": "Rèn cảm quan thẩm mỹ, chất liệu và xu hướng thời trang.",
    "Thiet ke noi that": "Học bố cục không gian, vật liệu và phối màu nội thất.",
    "Kien truc": "Học AutoCAD, SketchUp, và tham gia các dự án thiết kế.",
    "My thuat": "Phát triển khả năng tạo hình, phối màu và biểu đạt cảm xúc.",
    "Nhiếp anh": "Rèn bố cục, ánh sáng và kỹ thuật chụp ảnh.",
    "Dien anh": "Học quay dựng, kịch bản, hậu kỳ và kể chuyện bằng hình ảnh.",
    "Du lich": "Tìm hiểu điểm đến, văn hóa, dịch vụ và trải nghiệm khách hàng.",
    "Quan tri dich vu du lich va lu hanh": "Học vận hành tour, dịch vụ du lịch và chăm sóc khách hàng.",
    "Huong dan du lich": "Rèn thuyết trình, ngoại ngữ và kiến thức điểm đến.",
    "Thiet ke game": "Học thiết kế gameplay, đồ họa, tương tác và tư duy sáng tạo.",
    "Nghe thuat so": "Phát triển minh họa số, animation và sáng tạo đa phương tiện.",
    "Quay phim - Dung phim": "Học quay, dựng hậu kỳ, ngôn ngữ hình ảnh và kể chuyện bằng video.",
    "Dieu khien va quan ly tau bien": "Thực hành điều động, dẫn tàu, an toàn hàng hải, lập hải trình và xử lý tình huống trên biển.",
    "Khai thac may tau thuy va quan ly ky thuat": "Học buồng máy, động cơ tàu thủy, bảo dưỡng kỹ thuật, an toàn vận hành và tiết kiệm nhiên liệu.",
}
