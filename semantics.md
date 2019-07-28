# テンプレートの書き方

テンプレートでは論理記号を表すのに NLTK
<http://www.nltk.org/book/ch10.html>
の表記法を使っています。代表的なところだと、以下の記号が使えます。

| 名称 | 記号 |
|:-----------|:------------|
|  否定 |  -A  |
|  連言 |  A & B  |
|  選言 |  A \| B  |
|  条件法 | A -> B  |
|  全称量化 | forall x. A  |
|          | all x. A  |
|  存在量化 | exists x. A  |
|  等号    |  x = y  |
|  ラムダ   | \\x. A  |

具体例として、以下の文をとりあげます。
それぞれの論理式（意味表示）を導出できるようなテンプレートを考えます。

| 文 | 論理式 |
|:-----------|:--------------------|
|  John walked. | `walk(john)` |
|  John loves Susan. |  `love(john,susan)` |
|  John does not loves Susan. |  `-love(john,susan)` |
|  Someone walked. |  `exists x. walk(x)` |
|  Nobody walked. | `-exists x. walk(x)` |
|  Everyone walked. | `forall x. walk(x)` |
|  Some student walked. |  `exists x. (student(x) & walk (x))` |
|  No student walked. | `-exists x. (student(x) & walk (x))` |
|  Every student walked. | `forall x. (student(x) -> walk (x))` |
|  John loves a girl. | `exists x. (girl(x) & love(john,x))` |
|  A boy loves a girl.  | `exists x. (boy(x) & exists y. (girl(y) & love(x,y)))` |
|  No boy loves a girl. | `-exists x. (boy(x) & exists y. (girl(y) & love(x,y)))` |
|  Every boy loves a girl. | `forall x. (boy(x) -> exists y. (girl(y) & love(x,y)))` |

テンプレートは yaml 形式で記述されます。
まず、文末のピリオドを処理するため、次のテンプレートを書き込んだファイル
`templates_test.yaml` を作ります。

```
    - category: .
      semantics: \E X. X
      surf: "."
```

例として、次の推論を考えます。

```
    John walked.
    Nobody walked.
```

この二行を書き込んだ `example1.txt`というファイルを作ります。
この二文は矛盾しているため、正しい論理式が導出できれば、答えは "no"
になります。

```
    $ ./en/rte_en_mp_any.sh example1.txt en/templates_test_empty.yaml
```

この段階では、テンプレートはピリオドの処理しかしていないため、 結果は"unknown" となり、たとえば、C&Cパーザでは、次のようなCCG導出木が得られます。

[Example-1a](example1.txt.candc.empty.html)

このファイルは `example1.txt.candc.html`という名前で
`en_results`ディレクトリに生成されます。

テンプレートに何も記述していないのに、John, walked, nobody に意味が割り当てられているのは、統語範疇に対するデフォルトの意味割り当てが定義されているからです。しかし、このデフォルトの意味割り当てはあまり賢くないので当てにしてはいけません。

いまの例の場合、前提の "John walked." にはたまたま正しい`walk(john)`が割り当てられています。自動詞 walk の意味割り当てを明示的に書くためには、`S[dcl=true]\NP`
という統語範疇（素性を無視すれば、`S\NP`という統語範疇）のテンプレートを次のように書く必要があります。

```
    - category: S\NP
      semantics: \E x.E(x)
```

`\E x.E(x)`は`\E. \x. E(x)`の省略形です。
この`\E x.E(x)`の`E`の部分には、walked の基底形`walk`（walkedをlemmatizeした表現) が入ります。結果的に`\x.walk(x)`が walked のノードの意味割り当てとなります。

結論の "Nobody walked." の正しい意味表示は
`-exists x. walk(x)`です。統語範疇NPの nobody
には、`\P. -exists x. P(x)`
を割り当てる必要があります。これは次のようにテンプレートに書きます。

```
    - category: NP
      semantics: \E P. -exists x. P(x)
      surf: nobody
```

`\E P. -exists x. P(x)`の最初の引数`\E`は、`nobody`が入りますが、これはラムダ項の本体では使いません。よって、`\E.`は何も束縛していません。

意味合成は、CCGの組合せ規則によります。主に使うのは次の二つの関数適用規則です。

```
         X/Y : f    Y : a    
    fa --------------------
             Y : fa

         X : a    Y\X : f    
    ba --------------------
             Y : fa
```

意味合成では、合成する二つのノードのうちどちらが関数 `f`となり、どちらがその引数 `a`
となるのかが重要です。上の例では、ナイーブに意味割り当てを行うと次のようになります。

```
         NP : \P. -exists x. P(x)     S\NP : \x.walk(x)
    ba -------------------------------------------------
              S : (\x.walk(x))(\P. -exists x. P(x))
```

しかし、これでは`\x.walk(x)`の方が関数で、`\P. -exists x. P(x)`が引数となってしまうため、正しい意味表示は得られません。

教科書的には、次のような type-raising がどこかの段階で適用されて、主語の方の範疇が `S/(S\NP)`となっています。

```
         S/(S\NP) : \P. -exists x. P(x)     S\NP : \x.walk(x)
    ba -------------------------------------------------------
              S : (\P. -exists x. P(x))(\x.walk(x))
```

同じことを主語の統語範疇は`NP`のままでやろうとすると、意味論の方で工夫する必要があります。walk のような`S\NP` という範疇の自動詞に対する意味割り当てを次のように修正します。

```
    - category: S\NP
      semantics: \E Q.Q(\x.E(x))
```

これにより、導出木は、

```
         NP : \P. -exists x. P(x)     S\NP : \Q.Q(\x.walk(x))
    ba -------------------------------------------------------
              S : (\Q.Q(\x.walk(x)))(\P. -exists x. P(x))
```

となります。ここで得られたラムダ項をワンステップずつ簡約すると、

```
   (\Q.Q(\x.walk(x)))(\P. -exists x. P(x))
    --> (\P. -exists x. P(x))(\x.walk(x))
    --> -exists x. (\x.walk(x))(x))
    --> -exists x. walk(x)
```

となり、正しい意味表示が得られます。

`example1.txt`の場合、次のテンプレートで、上にあげたそれぞれの文に対する正しい意味表示を得ることができます。

```  
  - category: NP
    rule: lex
    semantics: \E F. F(E)
    child0_category: N

  - category: N
    semantics: \E. E
    pos: NNP

  - category: NP
    semantics: \E P. -exists x. P(x)
    surf: nobody

  - category: S\NP
    semantics: \E Q. Q(\x.E(x))

  - category: .
    semantics: \E X. X
    surf: "."
```

ここで、`pos: NNP`というのは John のような固有名詞の POS tag です。`category`にない情報を参照して意味割り当てを定義したいときは、このように`pos`を参照することができます。

```
  - category: NP
    rule: lex
    semantics: \E F. F(E)
    child0_category: N
```

は unary rule に対する意味を指定しています。これは、統語範疇`N`から`NP`に type-shift を行う`lex`という次のような規則規則です。

```
          N : A
   lex ---------------
         NP : \F.F(A)
```

`semantics: \E F. F(E)`の最初の引数`E`には、親ノードの意味表示`A`が入ります。

example1の推論に対して最終的に得られる意味表示は

[Example-1b](example1.txt.candc.html)

のようになります。

## テストセットの利用

テンプレートを拡張していくとき、基本的な構文を含むテストセットを用意しておくと便利です。

例えば、`example1.txt` に対して、その正解を `example1.txt.answer`というファイルに次のように書いておきます。

```
    no
```

例えば、他に次のような例を考えて、それぞれ `example2.txt`と`example3.txt`とします。正解はどちらも "yes" です。

```
Everyone walked.
John walked.
```

```
John loves a girl.
Someone loves a girl.
```

この問題と正解のペアを `testset/`というディレクトリを作って入れておきます。次のコマンドで、現在のテンプレートをこのテストセットに対して評価することができます。

```
    ./run_testset.sh <templates>
```

結果の一覧は、`en_results/main.html`から見ることができます。Dropbox にある `templates_test1.yaml`を使って、ccg2lambdaディレクトリで次を実行すると

```
    ./run_testset.sh en/templates_test1.yaml
```

[main.html](main.html) のようになります（ここでは、C&C, EasyCCG, depccgという三つのパーザを使っています）。