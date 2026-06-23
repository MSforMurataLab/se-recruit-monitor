"""matcher ユニットテスト"""

from monitor.matcher import analyze_text

SECONDARY = ["二次応募", "追加募集", "追加日程"]
SE = ["SE職", "システムエンジニア", "ソリューションエンジニア"]


def test_no_match_normal_page():
    text = "2027年度新卒採用の募集は終了いたしました。SE職の募集要項はこちら。"
    result = analyze_text(text, SECONDARY, SE)
    assert not result.matched


def test_match_secondary_and_se():
    text = "システムエンジニア職について追加募集を開始しました。エントリー再開。"
    result = analyze_text(text, SECONDARY + ["エントリー再開"], SE)
    assert result.matched
    assert "追加募集" in result.secondary_hits


def test_exclude_seminar_false_positive():
    text = "NRIセミナー追加日程の募集開始しました。システムエンジニア向けセミナーです。"
    result = analyze_text(text, SECONDARY, SE)
    assert not result.matched


def test_match_nijiji_obo():
    text = "SE職（システムエンジニア）の二次応募を受け付けます。"
    result = analyze_text(text, SECONDARY, SE)
    assert result.matched
