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

・フォビエイテッド圧縮
　-レンダリングの負荷軽減効果は減少する可能性があるが、ネットワーク負荷削減の効果は向上する可能性がある．
　-MPEG-DASHのビデオストリーミングにおいてフォビエイテッド圧縮は新しい．
・MPEG-DASHによる円形の高解像度適応
　-タイルではなく，焦点を中心に円形に映像品質を変更していく．
　-タイルよりも自然に低品質の領域を増やせる．
　-ユーザー体験が向上し、視覚的に違和感が少ない．
・ストリーミングアルゴリズムの最適化(AI・機械学習の応用)
　-異なるネットワーク条件下でのさらなる最適化．
　-ネットワーク環境を観測してフォビエイションした映像の品質を更に動的に変更していく．



2024.11.27
・MPEG-DASHのシステム設計を行った。
・まだ改良中
・Assets/Snow.mp4のアドレスにこの名前の動画を用意すると、デバッグできます。
