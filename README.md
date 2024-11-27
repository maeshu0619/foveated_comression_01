フォビエイテッド圧縮を行うプログラミングコードの基盤です。
このリポジトリにあるコードはまだ発展途上です。

◆現状のシステム
・H.264圧縮を行うことで、3種類の解像度の動画を用意。
・視線追跡の代わりにカーソルの位置をリアルタイムに読み取っている。
・カーソルの位置を中心に、高、中解像度の映像は円形に、低解像度は背景映像として重ねる。そのあと3層の映像を1層に合成する。
・ストリーミングシステムは未実装
・現在のネットワーク環境を観測するシステムの基盤
・ネットワーク環境をもとにグラフをプロットするシステムの基盤

◆今後の展望
・Pygameウィンドウではなくブラウザ上で映像の表示とストリーミングを行いたい。
・視線予測（これは難しいのでヒューリスティックな手法を模索する予定です）を用いて高解像度に表示する位置を決める。
・視線予測をもとに次の動画のセグメントを作成し、MPEG-DASH等を用いてhttpブラウザ上にキャストする。
・キャストする動画の品質をABR（適応型ビットレートの割り当て法）を用いて決定する。その為の機械学習のシステムの構築。

2024.11.27
・MPEG-DASHのシステム設計を行った。
・まだ改良中
・Assets/Snow.mp4のアドレスにこの名前の動画を用意すると、デバッグできます。
