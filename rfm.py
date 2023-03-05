###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
# Uçtan uca RFM tekniği ile müşteri segmentasyonu uygulaması gerçekleştireceğiz.
###############################################################
# Basamaklar;

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7. Tüm Sürecin Fonksiyonlaştırılması
# Yukarıda görmüş olduğumuz son başlıkta tüm yaklaşımları tek bir fonksiyonla tanımlayarak bir fonksiyonla
# iki satır kod yazarak bütün işlemleri otomatik bir şekilde yapabileceğimiz bir yapıyı hazırlayarak uygulamamızı tamamlamış olacağız.

###############################################################
# 1. İş Problemi (Business Problem)
###############################################################

# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Değişkenler
#
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir. (Bu veri seti ürünlere göre tekil, invoice lara göre çoklama. Ama ana odağımız invoic lar.)
# InvoiceDate: Fatura tarihi ve zamanı.                                                   (Bır faturanın içerisinde birden fazla ürün satılmış olabilir. )
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.


###############################################################
# 2. Veriyi Anlama (Data Understanding)
###############################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option("display.width", 500)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)         # Sayısal değişkenlerin virgülden sonra kaç basamağını göstermek istiyorsak.

df_ = pd.read_excel("C:/Users/Emre Bilir/Desktop/DSBootcamp/crmAnalytics/datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()
df.head()
df.shape
df.isnull().sum()
# 1.Sorumuz: 85048 numaralı ürüne toplam kaç para ödenmiştir? df.loc[0,"Quantity"] * df.loc[0, "Price"]
# 2.Sorumuz: Bu faturada toplam ne kadar fatura bedeli vardır? ....

# Customer ID si eksik olan gözlem birimlerini kaldırıcam. Çünkü müşterinin IDsi belli değilse müşteri özelinde segmentasyon çalışmaları yapacak olduğumdan dolayı, bu
# ölçülebilirlik değeri taşımadığından dolayı hepsini silmeyi tercih edicem.

# essiz urun sayisi nedir?
df["Description"].nunique()
# herbir üründen kaçar tane satılmış?
df["Description"].value_counts().head()
# en çok sipariş edilen ürün hangisidir?
df.groupby("Description").agg({"Quantity": "sum"}).head()
# Yukarıda bir problem olmuştur çünkü quantity - değer olamaz. Şimdilik bu problemi görmezlikten gelelim çünkü veri ön işleme bölümünde bu problemi ortadan kaldırmış olucaz.
# Biz ana amacımıza gidelim ve quantity i büyükten küçüğe sıralayalım.
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

## Eşsiz ürün sayısı 4681 adetti. Bu eşsiz ürünler faturalarda kaçar defa bir faturaya gündem oldu?
## Örneğin WHITE HANGING HEART T-LIGHT HOLDER isimli ürün 3549 kere belirli bir faturada geçmiş. Ama kaç tane geçmiş'i bilmiyorum. Kaç tane toplamda satın alınmış bilmiyorum.

# Kaç adet fatura bilgisi mevcut?
df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]                                  # Soru1 in cevabı
df.head()
# Fatura başına toplam harcanan parayla ilgilenirsek ne yapıyoruz?
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()                          # Soru2 nin cevabı


# Bu veri seti faturalara göre oluşturulmuş bundan dolayı çoklama gibi gözüküyor. Buradaki tekil birim stoklar, StockCode ları. Burada bizim odaklanacak olduğumuz durum
# kullanıcıların özelinde segmentasyon yapmak olduğundan, segmentasyona giderken bu tabloları tekilleştirmem gerekecek. Customer ID de mesela burada çoklamadır. Total_Price
#'da bir problem vardı. Bu tablonun yapısı itibariyle birim fiyat ve quantity bilgileri vardı dolayısıyla bunları çarptım ve değişken olarak ekledim. Sadece betimlemek adına da
# ınvoice lara göre groupby a aldım ve total_price ların toplamını aldık.
###############################################################
# 3. Veri Hazırlama (Data Preparation)
###############################################################

df.shape
df.isnull().sum()
# Burada yapılması gereken ilk şey bu customer ID ler eksik olduğundan dolayı bunları uçurmak olacak. Description bölümündeki eksik değer sayısı oldukça az bu yüzden göz ardı
# edilebilir.
# df = df[(df['Quantity'] > 0)]
df.dropna(inplace=True)
# 525461 gözlem birimi 417534 gözlem birimine düştü.
# RFM e outline temizliği yapmalı mıyız, yapabilir miyiz? Evet  yapılabilir. Fakat burada outlinerlar bizim için 5 skoruna denk geleceğinden dolayı eğer zaten aykırı değer
# çözümü olarak bir baskılama yapsaydık da aynı değere denk geleceğinden dolayı bu değer, aykırı değer incelemesini, analizini ya da düzeltmesini yapmamayı tercih edebiliriz.

# Başka ne yapıcaz? Veri seti hikayesinde şöyle bir problem vardı; invoice'da başında C olan ifadeler vardı. Bunlar iadeleri ifade etmektedir. Bunlar da bazı - değerlerin
# gelmesine sebep olmaktadır yukarıda gördüğümüz gibi.

# Önce bir özet istatistiklere bakalım. Quantity'de -9360 gibi bir değer var. Diğer yandan %75teki değer 12k iken max değer 19152k gibi uç bir değer. Bunlar aykırı değerlerdir
# zaten. Skorlaştıracağımız zaman bunların önemi kalmayacak. Fakat iade olan faturaları bi veri setimiz içerisinden çıkaralım bakalım durum nasıl deişecek. Çünkü describe'da
# hem quantity de hem price değişkeninde çeşitli problemlere sebep olmuş gibi gözüküyorlar. Total_price'da da aynı sorun var. Dolayısıyla öyle bir şey yapmalıyız ki iade edilen
# faturaları veri setinden çıkarmamız lazım.
df.describe().T
df = df[~df["Invoice"].str.contains("C", na=False)]

###############################################################
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
###############################################################
# Şimdi yapmamız gereken şey her bir müşteri özelinde  bu Recency, frequency ve monetary değerlerini hesaplamak olacak.
# Recency, Frequency, Monetary
df.head()
# Burada öncelikle analizi yaptığımız günü belirlememiz gerekmektedir. Bu ne anlama geliyor? Dikkatimizi çekmiş olacaltır ki veri seti 2009-2011 yılları arasında oluşturulan bir
# bir veri setidir. Dolayısıyla biz o yıllarda analizi yapmadığımız için bir yol izlememiz gerekmektedir. İlgili hesaplamaların yapılması için analizi yapıldığı günü tanımlama-
# mız gerekmtektedir. Örneğin bunu nasıl yapabiliriz; veri seti içerisindeki en son tarih hangi tarihse örneğin bu tarihin üzerine iki gün koyarız yani 2010,11,12 tarihini
# analiz yapılan tarih gibi kabul ederiz. Bu tarih üzerinden Recency 'i hesaplarız. Analizin yapıldığı tarih örneğin 2010-12-11 ise bir kullanıcı örneğin ayın 9 unda satın
# alma yaptıysa bunun üzerinden fark işlemine göre 2 gün 1 gün vs. şeklinde müşterilerin recency değerleri hesaplanmış olur. Buna yönelik olarak çalışmanın başına datetime
# kütüphanesi dahil ediyoruz.
df.info()
df["InvoiceDate"].max()

today_date = dt.datetime(2010, 12, 11)
type(today_date)
# today_date datetime formunda bir değişkendir. Bu da bize birazdan yapacak olduğumuz işlemlerde zaman açısından fark alabilme imkanını sağlayacak. Bugünün tarihini yani analizi
# yaptığımız gün olarak varsaydığımız tarihi oluşturduk. Şimdi ne yapmamız lazım? Aslında RFM analizinin temeli basit bir pandas operasyonudur.Burda bütün müşterilere göre
# groupby'a alıcaz. R,Fve M'i kolay bir şekilde hesaplicaz. Recency'de today_date'ten groupby aldıktan sonra herbir müşterinin max tarihini bulmamız lazım ve today_date'ten
# çıkardığımızda recency'i bulucaz. Ve yine benzer bir şekilde customer ID ye göre groupby'a aldıktan sonra herbir müşterinin eşsiz fatura sayısına gidersek müşterinin kaç
# tane işlem yaptığını buluruz,kaç tane satın alma yaptığını buluruz. Benzer bir şekilde yine customer ID ye göre groupby yaptıktan sonra Total_price'ların sum'ını alırsak da
# herbir müşterinin toplam kaç para bıraktığını hesaplamış oluruz.

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
# days attribute unu ekledik çünkü tarihsel bir değişken olduğu için bunu gün cinsinden ifade ettik.
rfm.head()
# İndexlerde customer ID ler var artık bunlar tekilleşmiş durumdadır.
# İsimlendirmeleri değiştirebiliriz.
rfm.columns = ['recency', 'frequency', 'monetary']

rfm.describe().T
# metriklerin değerlerine baktık monetary'nin max değeri dışında mantıksız bir değerle kaşılaşmadık ki skor oluşturacak olduğumuzdan dolayı yine de bir problem olmayacaktır.
# Yalnın monetory'nin min değerinin 0 olması tam olarak istediğimiz bir durum olmayabilir. Bunu uçurmamız gerekiyor.
rfm = rfm[rfm["monetary"] > 0]
# yeni setindeki müşteri sayısı da;
rfm.shape
# 4312 tane müşterimiz ve onları temsil eden metriklerimiz elimizde. Bunları skorlara çevirmek gerek.

###############################################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
###############################################################
# Dikkat etmemiz gereken nokta R ters, F ve M düz bir şekilde işlememiz gerekir.
# quantile cut fonksiyonuna böleceğimiz değişkeni verdik, kaç parçaya bölmek istediğimizi söyledik, bölme işlemi sonrasında label'ları, etiketleri verdik.
# qcut otomatik olarak değerleri küçükten büyüğe doğru sıralar.

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm.head()
# 0-100, 0-20, 20-40, 40-60, 60-80, 80-100
# Frequency' de bir miktar değişiklik yapmamız gerek. Aşağıdaki eklemeyi yapmazsak hata alırız. Oluşturulan aralıklarda unique değerler yer almamaktadır diyor.
# Öyle bir durum oluşmuş ki yukarıdaki örnek için söylüyorum; 0-20 arasında 1 ler var,20-40 arasında da 1 ler var diğerlerinde de var. Yani o kadar fazla tekrar eden frekans
# var ki küçükten büyüğe doğru sıralandığında çeyrek değerlere düşen değerler aynı olmuş. Yani örneğin daha doğru bir değişken de aralıklardaki değerler farklı olabilir.
# 0-20 dekiler 1 ,20-40takiler 2 vs gibi olabilecekke muhtemelen daha fazla sayıda aralığa hep aynı sayıda değerler denk gelecek şekilde ilerlemiş.
# Çözüm için rank metodunu kullanıyoruz. method=first diyerek ilk gördüğünü ilk sınıfa ata bilgisini vermiş olucaz.
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

# şimdi bu değerler üzerinde skor değişkeni oluşturmamız gerekiyor.R ve F değerlerini bir araya getirmemiz gerekiyor.Monetary'i niye hesapladık? Gözlemlemek için hesapladık.
# Hatırlayacak olursak 2 boyutlu görselde RFM skorlarına gitmek için R ve F değerleri yeterli olmaktaydı.
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
rfm.head()
# GÖzlemlediğimiz üzere iki ayrı değişkendeki int değerleri önce her bir değişkeni kendi içinde olacak şekilde string'e çevirdik sonra iki stringi toplama işlemi yapıp bunu
# yeni bir değişken olarak ata dedik. Şimdi özet istatistiğe bakıp bir durum değerlendirmesi yapalım.
rfm.describe().T
# örnek olarak istediğim skoru yazıyorum;
rfm[rfm["RFM_SCORE"] == "55"]
# şapiyon müşteri sayımız 457 adettir.

rfm[rfm["RFM_SCORE"] == "11"]
# bunları böyle tek tek mi yapıcaz. Bunlara şampiyon vs gibi şeyler yazalım direkt bilgimizi tabloya bakmadan anlamış olalım......
###############################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
###############################################################
# Önceki bölümlerde oluşturduğumuz bazı kodlar vardı. 55,11,25 gibi ve teorik bölümde görmüştük ki 2 eksen üzerindeki R ve F skorlarının kesişimlerinde oluşan, sektörde genel
# kabul gören bazı sınıflar vardı. Az önce numeric anlamda bazı değerlendirmeler yaptık ama bunların karşısına okunabilirliği arttırmak adına segmentlerin isimlerini yazabiliriz
# Dolayısıyla ben regular exprecion ifadelerini,regexleri, düzenli ifadeleri kullanarak çok basit bir şekilde yapıcaz. Regexi amacımız için kullanacağız. Dileyen detaylarına
# bakabilir. Biz R sinde 5 F sinde 5 gördüğüne şampiyon yaz ... gibi bir amaç için kullanıcaz.

# regex
# segment map' imizi getiriyoruz.

# RFM isimlendirmesi

# Şimdi çok basit bir kod yazıcaz.Dicez ki bu (r'....) regex'i (regular expression)ifade etmektedir. Bize şu sorguyu ve path'ı match etmeyi yani yapı yakalamayı sağlar.
# Neyi sağlar? 2 tane değer var RFM skor değişkenimizin içinde 11,55 gibi. Bu yöntemle şunu yapıcaz. Dicez ki 1. elemanında 1 ya da 2 2.elemanında 1 ya da 2 görürsen şu
# isimlendirmeyi yap.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
# Şimdi bu durumu veri setimize uygulayalım. Bunu replace metoduyla yapıcaz. Bu metoda argüman olarak regex ifadesi vericez. Böylece skorları birleştirmiş olcaz.
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

# Şuanda daha okunabilir bir şekilde, sayılar yerine daha anlaşılır bir formatta string ifadelerle neyin ne olduğu bilgisini gönderdik.

# Peki bu segmentleri oluşturdum şimdi ne yapıcam? Öncelikle oluşturulan bu segmentlerin bir analizini yapmak lazım. Yani ilgili takım lideri, departmanlar vs. bunlar bi
# bilgilendirilmeli. Denmeli ki bizim şu sınıflarımız var, bu sınıfların özellikleri de bunlardır. Ne gibi özellikler? Örneğin bu sınıflardaki kişilerin recency ortalamaları
# ne? frequency ortalamaları ne? gibi bazı temel bilgilere erişmek istiyor olabilirz. Hemen erişelim.
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])
# !!!!! dikkat bunlar metriklerdir, skorlar değil. Bunların şimdi ortalamalarını alarak segmentleri arasında bir karşılaştırma yapıcaz.
# Bu şekilde sonuçtan bakarak segmentleri betimleyebiliriz. Segmentleri analiz et nedir? Bu şekilde yapılarını anlamaya çalışmak demektir. Örneğin chamipons sınıfa bakalım
# normalde diğer bütün metriklere göre daha iyi bir durumda olmasını beklerim. Bir doğrulama da yapmaya çalışıyoruz ayın zamanda. R değeri diğerlerine göre en düşüğüdür.
# bana en yakın müşteriler yani. !!!! şuanda skorlarda değil gerçek değerlerdeyiz. new_customers R değeri düşük çünkü yeni geldiler bunlar. Acaba bunları birbirinden ne ayıracak?
# championsun F değeri ortalama 12 imiş. Yani bu champions grubunda 663 kişi var bu kişilerin 8,9,11,10 gibi çeşitli frekansları var. bunların ort u 12ymiş. New customers ın
# ise 1 miş. E bunlar yeni müşteri zaten. Burda bir potansiyel tanımını da yapmış olur ve bu müşterilere odaklanmış olabiliriz mesela.

# İşimiz bitti mi? HAYIR. Diyelim ki satış pazarlama takımının lideri şu talepte bulunuyor: biz senin anlattıklarından ikna olduk, müşterilerimizle ilgilenmemiz gerektiğini
# düşünüyoruz.Ki zaten bunu biliyorduk ama nasıl odaklanmamız gerektiğini mantıksal bir yere koyamıyorduk. Sen şimdi bize need_attention sınıfını ver. Biz bu sınıfa özellikle
# odaklanmak istiyoruz. Eğer bu sınıf ilgi görmez ise bunun gideceği yer churn dür yani terktir. Önce uykuya sonra bizi komple terk etme durumuna geçecektir. Ya da başka bir
# senaryo; kaybedemeyeeğimiz sınıf ya da at_risk gibi sınıflarla ilgilenmek istiyor olabiliriz. Dolayısıyla bir departman bizden bu sınıfa erişmek istiyor olabilir. Ne
# yapmamız lazım? E bunları seçip, index bilgileri customerID leri ilgili departmana göndeririz ve ya bir veri tabanına yazarız. Böylece o kişilere erişip ilgili iletişimi
# sağlayabilirler. Hemen seçelim.
rfm[rfm["segment"] == "cant_loose"].head()
# Bunların index bilgisini yani ID lerini aslında, istersek;
rfm[rfm["segment"] == "cant_loose"].index
# şimdi de ilgili departmanın anlayabileceği türden göndermemiz lazım. yeni bir dataframe oluşturup içerisine örneğin yeni müşterileri atmak isteidğimizi düşünelim.
new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index
# bu ID lerde ondalıklar var gözümü yordu dersek int e çevirebiliriz.
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

# hala bu bizim onlara verebileceğimiz bir formatta değil. Bir excell ya da csv formunda bunu dışarıya çıkarmamız lazım.
new_df.to_csv("new_customers.csv")
# dosyamız geldi. şuan bunu ilgili departmana ilettiğimizde bu departman bu ID lere göre bu yeni müşteriler ve bunlara bir şeyler yapalım, kendileri gelmiş. Bize maaliyetleri
# yok. Hemen bir kampanya yapalım gibi yorumlara erişebilirler. Ya da bu sonuçlar bir database e basılır yani bir tablo haline getirilir ve o tabloda oluşturduğumuz bütün
# segmentler yer alır. Yine o tabloyla konuşan bir tablo power BI gibi iş zekası aracı, seçimler yaparak çok kolay bir şekilde yani bana şı segmenti getir betimsel istatistik
# lerini görster gibi seçimler yaparak ilgili arayüzlerden bu bilgilere erişebilir. Bizim burdaki görevimiz ilgili segmentleri oluşturmak ve bunları dışarıya çıkarmak.

# Burada örneğin oluşturmuş olduğumuz rfm i de komple çıkarmak isteyebiliriz ki genelde bu daha yaygın olarak karşımıza gelebilir. Bunu çıkartırsak bütün segment bilgileri gider
rfm.to_csv("rfm.csv")

###############################################################
# 7. Tüm Sürecin Fonksiyonlaştırılması
###############################################################
# !!!!! Bütün sürecin bir scripte çevrilmesi diye de olabilirdi başlığımız.
# Buraya normalde bir fonskiyon yazdığımızda bu fonksiyonun temel programlama prensiplerince taşıması gereken bazı özellikler olur. Do one thing prensibi gibi. Dont repeat
# yourself gibi. Bir diğeri de modüler olması gibi. Dolayısıyla bizim rfm analizi kapsamında yaptığımız bir çok basamak var,bir çok işlem var. Normalde burdaki bütün
# işlemler için ayrı ayrı fonksiyon yazmak fonksiyon yazma çervesinde daha verimli olabilir. Fakat bizim burdaki temel değerlendirme yaklaşımımız şu olacak: Biz bir script
# yazıyoruz. Özetle bbunu da bir fonksiyonla temsil ediyoruz. Dolayısıyla bu fonksiyonu çağırdığınızda ve bu fonksiyona belirli bir dataframe' i sorduğumuzda çok seri bir
# şekilde bütün analiz işlemleri tamamlansın diye bir sonuç basılsın istiyoruz. İşlemi gerçekleştirelim.
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
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()

rfm_new = create_rfm(df, csv=True)
# Başarılı bir şekilde bütün müşterilerin segmentlerine ayrıldığı ve ayrılmış olan son dataframe elime gelmiş oldu. Biraz daha özellik eklemek istersek bunu detaylandıralım;
# Örneğin Customer ID ler integer olarak gelse daha iyi olurdu. fonksiyon içine 306. kod satırına yazdık.
# Bİr de bu çıktının csv sini de mi oluştursak? rfm to csv bölümünü bu fonksiynumuza bir özellik olarak ekleyelim. 308.kod satırı.

# Başka neler ypaılabilir?
# !!!!!!! 1-) alt parçalara göre hazırlanabilir. her basamak için ayrı ayrı fonksiyonlar yazılabilir. bu fonksiyonlar ayrı ayrı yazıldıktan sonra ara işlemlere müdehale etme
# hakkı buluruz. Bunu parçalamak ne işe yarar? veri setinde değişiklik olabilir, yapısal bazı durumlar ortaya çıkabilir, ya da biz akış esnasında bu fonksiyonun basamaklarına
# müdehale etmek istiyor olabilir. Dolayısıyla bu bölümleri ayrı ayrı yaparsak ve hepsi return olup diğer fonksiyona girdi olacak şekilde akarsa bu durumda o ara katmanlara
# daha müdehale edilebilir bir hal olur. Bu duruma göre tercih edilebilir.

# 1-) Bu analiz dönem dönem tekrar edilebilir. Bu şu anlama gelir: Örneğin biz belirli bir yılın belirli bir ayında bu segmentleri oluşturduğumuzda bu segmentlerin içerisinde
# yer alan müşteriler bir sonraki ay ya da 3-6 ay sonra gibi periyotlarda değişebilir. Dolayısıyla burdaki değişimleri gözlemlemek oldukça kritikrir, değerlidir. Yani örneğin
# bu işi bizim her ay çalıştırabiliyor olmamız lazım daha kolay bir şekilde. Her ay çalıtırdıktan sonra çalıştırma işlemleri sonrasında oluşan segmentlerdeki değişimleri
# raporlayabilmeli ve örneğin ilk ay bir rapor oluşturduk belirli bir departmana aksiyon alması için bir liste gönderdik. o departman aksiyon aldı da bunun sonrası ne olacak?
# RFM segmentasyonu yapabilen bile bir çok şirkette bu bir problem noktasıdır. Aşılmaya çalışılan bir bariyerdir. Yani RFM i yaptık ve ya diğer bazı yöntemlerle bazı segmentlere
# ayırdık, aksiyon için ilgili departmanlara gönderdik. Aksiyon alındı tamam. Sonra? Takip etme problemimiz vardır. Dolayısıyla yapılması gerekilen şey bir kişi bu segmentasyon
# CRM işlerine girdiğinde bir ayağı hep burda kalmak zorundadır. Çünkü 1-2 ay sonra o verdiği aksiyon tavsiyelerinin sonucu ne olacak? kim değerlendirecek? bitti kenara at yapa-
# mayacak olacağız.Dolayısıyla aylara göre tekrar bu analizleri tekrar edip segmenler arasında, yapılan aksiyonlar arasında değişimler var mı? değişimi yapanlar kimler? bu bize
# nasıl bir katkı sağlamış? yeni aksiyonlar ne olabilir? başarılı olduk mu? bizi terk etmek üzere risk sınıfına giren müşteriler artık potansiyel sadık sınıfına umut vaad eden
# duruma geldi mi gibi durumları da zaman göre analiz etmemiz gerekmektedir. Bu işin analitik kısmında da zaman göre bu analizleri tekrar edip her dönemde elde ettiğimiz
# sonuçları bu csv ya da excel dosyalarını saklayıp bunları zamana göre de analiz edebiliyor olmamız lazım.








