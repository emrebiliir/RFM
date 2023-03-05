# RFM Tekniği ile Müşteri Segmentasyonu Uygulaması
# Uçtan uca RFM tekniği ile müşteri segmentasyonu uygulaması gerçekleştireceğim.

# Basamaklar;

# 1. İş Problemi
# 2. Veriyi Anlama
# 3. Veri Hazırlama
# 4. RFM Metriklerinin Hesaplanması
# 5. RFM Skorlarının Hesaplanması
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi
# 7. Tüm Sürecin Fonksiyonlaştırılması

# 7. basamakta, tüm yaklaşımları tek bir fonksiyonla tanımlayarak bütün işlemleri otomatik bir şekilde yapabileceğim bir yapıyı hazırlayarak uygulamamı tamamlamış olacağım.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 1. İş Problemi

# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi:
# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir. (Bu veri seti ürünlere göre tekil, invoice lara göre çoklama. Ama ana odağımız invoic lar.)
# InvoiceDate: Fatura tarihi ve zamanı. (Bir faturanın içerisinde birden fazla ürün satılmış olabilir. )
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 2. Veriyi Anlama

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option("display.width", 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)                                                # Sayısal değişkenlerin virgülden sonra kaç basamağını göstermek istiyorsam o değeri girdim.

df_ = pd.read_excel("/kaggle/input/online-retail-ii/online_retail_II.xlsx", sheet_name="Year 2009-2010")   # Dosyanın 2009 ile 2010 tarihleri arasındaki tarihleri almak istediğimi belirttim.
df = df_.copy()                                                                                            # Orijinal veri setinden değil de kopyası üzerinden işlemleri gerçekleştireceğim.
df.head()

# Toplam farklı ürün sayısı;
df["Description"].nunique()

# Her ürünün satıldığı adet bilgisi;
df["Description"].value_counts()

# En çok sipariş edilen ürün;
df.groupby("Description").agg({"Quantity": "sum"}).head()

# ! Dikkat. Quantity değerli olamaz. Şimdilik bu problemi görmezlikten gelicem. Çünkü veri ön işleme bölümünde bu problemi ortadan kaldırmış olucam. Ana amacıma doğru gidiyorum ve Quantity' i büyükten küçüğe sıralayacağım.

df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity",ascending=False).head()

# Toplam farklı ürün sayısı 4681 adetti. Bu eşsiz ürünlerin kaçar defa bir faturaya gündem olduğunu hesaplayacağım.
# Örneğin 'WHITE HANGING HEART T-LIGHT HOLDER' isimli ürün 3549 kere belirli bir faturada geçmiş. Kaç faturada geçtiğini ve kaç tane toplamda satın alındığını hesaplayacağım.

# Toplam fatura bilgisi adedi;
df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]          # Faturalardaki her ürün için ödenilen toplam miktar işlemi için her gözlem birimindeki ürünün satın alınan adet sayısı ile ürünün birim fiyayını çarpıp değer olarak bir değişkene atadım.
df.head()

# Her farklı faturada harcanan toplam miktar;
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()

# Bu veri seti faturalara göre oluşturulmuş bundan dolayı çoklama durumu söz konusudur. Buradaki tekil birim 'StockCode' lardır. Burada odaklanacak olduğum durum kullanıcıların özelinde segmentasyon yapmak
# olduğundan, segmentasyona giderken bu tabloları tekilleştirmem gerekecek. Mesela 'Customer ID' de çoklamadır. Bu tablonun yapısı itibariyle 'Price' ve 'Quantity' bilgileri vardı dolayısıyla bunları
# çarptım ve değişken olarak ekledim. Sadece betimlemek adına da 'Invoice' lara göre groupby' a alıp total_price' ların toplamını aldım.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 3. Veri Hazırlama

# Burada yapacak olduğum ilk şey 'Customer ID' ler eksik olduğundan dolayı bunları uçurmak olacak. 'Description' bölümündeki eksik değer sayısı oldukça az bu yüzden göz ardı edeceğim.

df.dropna(inplace=True)
df.shape                        # Veri setinin ilk halinde toplamda 525461 gözlem biri vardı. Eksik değerleri uçurduktan sonra gözlem birimi sayısı 417534' e düşmüştür.

# RFM analizimde aykırı değerleri temizlemeyeceğim çünkü onlar benim için 5 skoruna denk gelecek. Veri seti hikayesinde şöyle bir problem vardı; 'Invoice'da başında C olan ifadeler vardı. Bunlar iadeleri ifade etmektedir.
# Bunlar da bazı negatif değerlerin gelmesine sebep olmaktadır. Bu durum en çok sipariş edilen ürün işlemi sonucunda görülmüştü.
# Öncelikle bir özet istatistiklere bakacağım.

df.describe().T
# Quantity'de -9360 gibi bir değer var. Diğer yandan %75teki değeri 12.000 iken max değeri 19152.000 gibi uç bir değer olduğunu görüyorum. Bunlar aykırı değerlerdir.
# Skorlaştıracağım zaman bunların önemi kalmayacaktır. Fakat iade olan faturaları veri setinin içerisinden uçurayım ve durumun nasıl değişeceğine bakayım. Çünkü describe'da hem
# 'Quantity' de hem 'Price' değişkeninde çeşitli problemlere sebep olmuş gibi gözüküyor. 'Total_price'da da aynı sorun var.

df = df[~df["Invoice"].str.contains("C", na=False)]           # Faturalar arasında içerisinde 'C' ifadesini barındıranlar True, barındıramayan ve NaN değer olanlar False ifadesini alacak. ~ sembolü kullanmasaydım bana True değerleri yani içerisinde 'C' ifadesini barındıranları döndürecekti. ~ sembolünü kullandığımdan bunlar dışındakileri döndür demiş oldum. Ve dönen dataframe ile df isimli dataframe' imimi güncelledim.

df.shape                                                      # Gözlem birim sayısının düştüğünü gözlemledim.

df.describe().T                                               # 'Customer ID' deki iade edilen faturaları çıkarınca problem çözüldü.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 4. RFM Metriklerinin Hesaplanması

# Şimdi yapacağım şey her bir müşteri özelinde recency, frequency ve monetary değerlerini hesaplamak olacak. Burada öncelikle analizi yaptığım günü belirleyeceğim. Dikkatinizi çekmiş olacaltır ki veri seti
# 2009-2011 yılları arasında oluşturulan bir veri setidir. Dolayısıyla o yıllarda analiz yapmadığım için bir yol izlemem gerekmektedir. İlgili hesaplamaların yapılması için analizi yapıldığı günü tanımlamam
# gerekmtektedir. Buna yönelik olarak çalışmamın başına datetime kütüphanesi dahil ediyorum.

df.info()                                               # InvoiceDate değişkeninin tipinin datetime olduğunu görüyorum.

df["InvoiceDate"].max()                                 # En son kesilen faturanın tarihine bakıyorum.


# Analiz günümü belirliyorum ve tipini kontrol ediyorum.
today_date = dt.datetime(2010, 12, 11)
type(today_date)
# today_date datetime formunda bir değişkendir bu da bana birazdan yapacak olduğum işlemlerde zaman açısından fark alabilme imkanını sağlayacak. Bugünün tarihini yani analizi yaptığım gün
# olarak varsaydığım tarihi oluşturdum. Şimdi bütün müşterilere göre groupby'a alıp R, F ve M' yi kolay bir şekilde hesaplayacağım.

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

# Recency değeri için 'today_date'ten groupby aldıktan sonra herbir müşterinin max tarihini bulmam lazım ve 'today_date'ten çıkardığımda recency değerini bulacağım. Bu adımın döndürdüğü şey tarihsel bir
# değişken olduğu için '.days' ile bunu gün cinsinden ifade ettim.. Yine benzer şekilde 'Customer ID' ye göre groupby'a aldıktan sonra herbir müşterinin eşsiz fatura sayısına gidersem müşterinin kaç
# tane işlem, satın alma yaptığını bulurum. Benzer bir şekilde yine 'Customer ID' ye göre groupby yaptıktan sonra 'Total_price'ların toplamını alırsam da her bir müşterinin toplam kaç para bıraktığını hesaplamış olurum.

rfm.head()                                                 # İndexlerde 'Customer ID' ler var ve artık bunlar tekilleşmiş durumdadır.

rfm.columns = ['recency', 'frequency', 'monetary']        # Değişken isimlendirmelerini değiştirdim.
rfm.head()

rfm.describe().T
# Metriklerin değerlerine baktım monetary' nin max değeri dışında mantıksız bir değerle kaşılaşmadım ki skor oluşturacak olduğumdan dolayı yine de bir problem olmayacaktır.
# Yalnız monetory'nin min değerinin 0 olması tam olarak istediğim bir durum olmayabilir. Bunu uçuracağım.

rfm = rfm[rfm["monetary"] > 0]
rfm.describe().T

rfm.shape                                     # Oluşan yeni veri setindeki müşteri sayısı 4312 kişidir.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 5. RFM Skorlarının Hesaplanması

# R ters, F ve M düz bir şekilde işleyeceğim. 'Quantile cut' (qcut) fonksiyonuna böleceğim değişkeni ve kaç parçaya bölmek istediğimin bilgileriyle birlikte bölme işlemi sonrasında etiketleri de
# verdim. qcut fonksiyonu otomatik olarak değerleri küçükten büyüğe doğru sıralar.

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm.head()

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm.head()

# Frequency' de bir miktar değişiklik yapmam gerek. Aşağıdaki eklemeyi yapmazsam hata alırım. Bunun sebebi şudur; o kadar fazla tekrar eden frekans var ki küçükten büyüğe doğru sıralandığında
# çeyrek değerlere düşen değerler aynı olmuş. Çözüm için rank metodunu kullanacağım. 'method=first' diyerek ilk gördüğünü ilk sınıfa ata bilgisini vermiş oluyorum.
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm.head()
# Şimdi bu değerler üzerinden bir skor değişkeni oluşturmam gerekiyor. Bunun için R ve F değerlerini bir araya getireceğim. Monetary'i dahil etmiyorum. Hesaplamamın
# sebebi gözlemekti. 2 boyutlu görselde RFM skorlarına gitmek için R ve F değerlerini hesaplamak yeterlidir.

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))       # İki ayrı değişkendeki int değerleri önce her bir değişkeni kendi içinde olacak şekilde string'e çevirdim sonra iki stringe toplama işlemi yapıp bunu yeni bir değişken olarak atadım.
rfm.head()

# Artık istediğim skoru elde edebilecek seviyedeyim. Örneğin 55 skoruna dahip şampiyon müşteriye erişeyim;
rfm[rfm["RFM_SCORE"] == "55"].head()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 6. RFM Skorlarının Hesaplanması

# 2 boyutlu görsele bakmadan dataframe üzerinden hangi skorun hangi sınıfa ait olduğunu anlamak için sınıf bilgisini sütun olarak ekleyeyim. Sektörde genel kabul gören bazı sınıflar var. Az önce numeric anlamda
# bazı değerlendirmeler yaptım. Şimdi de bunların karşısına okunabilirliği arttırmak adına segmentlerin isimlerini yazacağım. 'Regular expression' ifadelerini (regex) kullanarak çok basit bir
# şekilde gerçekleştireceğim. Örnek olarak; 'R sinde 5 F sinde 5 gördüğüne şampiyon yaz' ... gibi bir amaç için kullanacağım.

# regex

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'hibernating',                              # (r'....) regex'i (regular expression)ifade etmektedir. Bize solundaki sorguyu ve sağındaki path'ı match etmeyi yani yapı yakalamayı sağlar.
    r'[1-2][3-4]': 'at_Risk',                                  # Örneğin 1. elemanında 1 ya da 2, 2. elemanında 1 ya da 2 görürsen 'hibernatin' isimlendirmesini yap.
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# Durumu replace metoduyla veri setimize uyguladım. Metoda argüman olarak regex ifadesi verdim. Böylece skorları birleştirmiş olcaz.
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

# ! Bunlar metriklerdir, skorlar değil. Bunların şimdi ortalamalarını alarak segmentleri arasında bir karşılaştırma yapıcam. Bu şekilde sonuçtan bakarak segmentleri betimleyebileceğim.
# Şuanda skorlarda değil gerçek değerlerdeyiz.
# Bundan sonra pazarlama stratejisi için son aşamayı hazırlama kısmı var. Örnek olarak 'cant_loose' segmentindeki müşterileri ilgili departmana vermek istediğimde;
new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index
# ID lerdeki ondalıklardan kurtulmak için int' e çevirdim.
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)
# İlgili departmana gönderebileceğim format olan csv şekline dönüştürüyorum.
new_df.to_csv("new_customers.csv")

# Eğer bütün segmentlerin müşterilerini iletmek istersem;
rfm.to_csv("rfm.csv")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 7. Tüm Sürecin Fonksiyonlaştırılması

# Bütün süreci bir scripte çevriyorum. Rfm analizi kapsamında yaptığım bir çok basamak var. Normalde burdaki bütün işlemler için ayrı ayrı fonksiyon yazmak fonksiyon yazma çervesinde
# daha verimli olabilir. Fakat benim burdaki temel değerlendirme yaklaşımım; Ben bir script yazıyorum. Özetle bunu da bir fonksiyonla temsil ediyorum. Dolayısıyla bu fonksiyonu çağırdığımda
# ve bu fonksiyona belirli bir dataframe' i sorduğumda çok seri bir şekilde bütün analiz işlemleri tamamlansın diye bir sonuç basılsın istiyorum.

def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)                                      # Ek olarak 'Customer ID' deki değerleri integer olmasını istedim.

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()                  # işlem yapılmamış halini tekrar çağırıyorum.

rfm_new = create_rfm(df, csv=True)
# Başarılı bir şekilde bütün müşterilerin segmentlerine ayrılmış olan son dataframe elime gelmiş oldu.
