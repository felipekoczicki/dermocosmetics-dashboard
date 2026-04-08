# 📋 Documento de Planos de Ação — UX/UI
## Site: cicatribem.com.br
**Data da análise:** Abril de 2026  
**Responsável pela análise:** Claude (Anthropic)  
**Versão:** 1.0

---

## 📌 Contexto

Este documento foi gerado a partir de uma auditoria completa de UX (Experiência do Usuário)
e UI (Interface do Usuário) realizada no site cicatribem.com.br.

A auditoria cobriu:
- Homepage (hero, carrosséis de produtos, seção de depoimentos, FAQ, footer)
- Página de produto (galeria, informações, CTA, volume discount, avaliações)
- Página de coleção (listagem, filtros, ordenação)
- Página institucional "Nossa História"
- Menu de navegação (desktop e mobile)
- Acessibilidade, performance e SEO on-page

Os problemas foram classificados por impacto, esforço e urgência,
resultando em 20 ações divididas em 3 horizontes de prazo.

---

# ⚡ CURTO PRAZO — 0 a 30 dias

> Ações de baixo esforço técnico e alto impacto imediato.
> Podem ser executadas pelo time interno ou desenvolvedor Shopify júnior.

---

### AÇÃO 01 — Corrigir espaço em branco na homepage

**Categoria:** UX / Performance Visual  
**Prioridade:** 🔴 Crítica  
**Esforço:** Baixo  
**Impacto:** Alto  

**Problema identificado:**  
Após o hero banner da homepage, há um espaço em branco extenso antes dos
carrosséis de produtos. Isso é causado por animações de scroll-reveal com
delay excessivo e/ou configuração de altura máxima dos slides no tema Shopify.
Usuários que rolam a página veem uma área cinza vazia e podem interpretar
como erro ou lentidão, aumentando a taxa de rejeição.

**Objetivo:**  
Eliminar o espaço vazio entre o hero e os carrosséis de produtos,
garantindo que o conteúdo seja visível imediatamente após o banner.

**O que fazer:**  
1. Acessar o Shopify Admin > Temas > Personalizar (Customize).
2. Localizar a seção do Slideshow e verificar a altura mínima configurada.
   Reduzir ou alterar para "Adaptar ao conteúdo" (Fit content).
3. Localizar as seções de carrossel (Lançamentos, Mais Vendidos) e
   verificar se há configurações de animação de entrada ativadas.
   Desativar ou reduzir o delay das animações para 0ms.
4. Caso o tema use JavaScript customizado com Intersection Observer
   para animar seções, localizar o arquivo `theme.js` ou similar e
   reduzir o `threshold` e o `delay` das animações de reveal.
5. Testar em modo de navegação anônima após as alterações.

**Responsável sugerido:** Desenvolvedor Shopify ou Gestor de E-commerce  
**Tempo estimado:** 2 a 4 horas  

**Critério de sucesso:**  
Ao rolar 1 scroll abaixo do hero banner, o primeiro carrossel de produtos
(Lançamentos) deve ser imediatamente visível, sem espaço em branco maior
que 20px entre as seções.

---

### AÇÃO 02 — Corrigir banners do hero no mobile

**Categoria:** UI / Responsividade  
**Prioridade:** 🔴 Crítica  
**Esforço:** Baixo  
**Impacto:** Alto  

**Problema identificado:**  
O banner do hero "Desconto Progressivo — Mês do Consumidor" tem o texto
"10% OFF — 2 Produtos" cortado na borda direita em viewports mobile (< 430px).
O design dos banners foi feito para desktop e não possui versão mobile adaptada.
Como a maioria do tráfego de cosméticos é mobile, isso compromete a comunicação
das principais campanhas.

**Objetivo:**  
Garantir que todos os banners do hero exibam 100% do conteúdo visual
em dispositivos mobile, sem corte ou overflow.

**O que fazer:**  
1. Para cada slide ativo no hero banner, criar duas versões de imagem:
   - Desktop: proporção 16:5 (ex.: 1440x450px)
   - Mobile: proporção 3:4 ou 1:1 (ex.: 750x1000px)
2. No Shopify Admin > Personalizar > Slideshow, configurar cada slide
   para usar a imagem mobile quando o breakpoint for < 768px.
   (A maioria dos temas Shopify modernos suporta "Imagem para mobile"
   separada por slide.)
3. Ao criar as imagens mobile, garantir que todo o texto informativo
   esteja dentro da zona segura central (safe zone) da imagem,
   longe das bordas laterais.
4. Alternativa mais rápida: no CSS do tema, adicionar para o hero:
   `object-fit: contain` ao invés de `cover` em mobile,
   ou reduzir o `font-size` dos textos sobrepostos via media query.

**Responsável sugerido:** Designer Gráfico + Desenvolvedor  
**Tempo estimado:** 4 a 8 horas (criação das artes + implementação)  

**Critério de sucesso:**  
Em um iPhone 14 (390px) e Samsung Galaxy S23 (393px), todos os textos
e elementos visuais dos banners estão completamente visíveis,
sem corte, overflow ou scroll horizontal.

---

### AÇÃO 03 — Adicionar botão de WhatsApp flutuante

**Categoria:** UX / Conversão  
**Prioridade:** 🔴 Alta  
**Esforço:** Baixo  
**Impacto:** Alto  

**Problema identificado:**  
O site não possui canal de atendimento rápido visível. Clientes com dúvidas
sobre modo de uso, prazos de entrega ou indicação de produto precisam
procurar o contato no footer. Isso aumenta o abandono de compra
por indecisão não resolvida.

**Objetivo:**  
Oferecer um ponto de contato rápido e acessível em todas as páginas,
reduzindo o abandono por dúvida e aumentando a confiança na compra.

**O que fazer:**  
1. Instalar um app de WhatsApp na Shopify App Store.
   Opções gratuitas/freemium recomendadas:
   - "WhatsApp Chat + Abandoned Cart" (by Softpulse Infotech)
   - "Tidio Live Chat & AI Chatbots"
   - "BLOOP: WhatsApp Chat Button"
2. Configurar o número de WhatsApp da Cicatribem.
3. Definir uma mensagem pré-preenchida contextual, por exemplo:
   "Olá! Tenho uma dúvida sobre os produtos Cicatribem 😊"
4. Posicionar o botão no canto inferior direito da tela.
5. Configurar o horário de atendimento visível no tooltip do botão
   (ex.: "Atendimento: seg-sex 9h-18h").
6. Em mobile, garantir que o botão não sobreponha o botão
   "Adicionar ao carrinho" nas páginas de produto.

**Responsável sugerido:** Gestor de E-commerce / Atendimento  
**Tempo estimado:** 1 a 2 horas  

**Critério de sucesso:**  
O botão de WhatsApp está visível em todas as páginas do site,
ao clicar abre o WhatsApp com a mensagem pré-configurada,
e não bloqueia nenhum elemento de navegação ou compra.

---

### AÇÃO 04 — Preencher alt text descritivo nas imagens de produto

**Categoria:** Acessibilidade / SEO  
**Prioridade:** 🟡 Alta  
**Esforço:** Baixo  
**Impacto:** Médio  

**Problema identificado:**  
11 imagens estão sem atributo `alt` e 16 imagens têm `alt` vazio ("").
Isso impede que screen readers (tecnologias assistivas para deficientes visuais)
descrevam os produtos. Também representa uma oportunidade perdida de SEO,
já que o Google usa o `alt` para indexar imagens no Google Imagens.

**Objetivo:**  
Garantir que todas as imagens de produto tenham descrição textual
relevante e otimizada para SEO.

**O que fazer:**  
1. Acessar Shopify Admin > Produtos.
2. Para cada produto, clicar na imagem e preencher o campo
   "Texto alternativo" (alt text).
3. Usar o padrão: `[Nome do Produto] [Tamanho] Cicatribem — [Contexto da imagem]`
   Exemplos:
   - "Creme Antiestrias Regenerador Dérmico 150g Cicatribem — Vista frontal do produto"
   - "Creme Antiestrias Cicatribem 150g — Mulher grávida aplicando o produto na barriga"
4. Evitar textos genéricos como "imagem1.jpg" ou repetição exata do nome da página.
5. Para as imagens de lifestyle (modelos usando o produto), descrever
   a ação: ex. "Mulher aplicando o Clareador Dérmico Cicatribem no rosto".
6. Repetir o processo para as imagens dos banners no hero slider,
   seções de "Antes/Depois" e imagens de depoimentos.

**Responsável sugerido:** Gestor de E-commerce  
**Tempo estimado:** 3 a 5 horas  

**Critério de sucesso:**  
100% das imagens de produtos têm `alt` preenchido com descrição
relevante. Verificar via: Shopify Admin > Relatórios > SEO,
ou usando a extensão gratuita "axe DevTools" no Chrome.

---

### AÇÃO 05 — Corrigir nome exibido dos produtos "KitDuplinha" e "KitTudo"

**Categoria:** UI / Qualidade  
**Prioridade:** 🟢 Baixa  
**Esforço:** Baixo  
**Impacto:** Baixo  

**Problema identificado:**  
Os produtos "Kit Duplinha" e "Kit Tudo" aparecem com o nome sem espaço
("KitDuplinha", "KitTudo") em certas seções dos carrosséis da homepage.
Isso dá aparência de erro/descuido e pode reduzir a credibilidade da marca.

**Objetivo:**  
Garantir que todos os nomes de produto sejam exibidos corretamente
com espaçamento adequado em toda a loja.

**O que fazer:**  
1. Acessar Shopify Admin > Produtos > localizar "Kit Duplinha" e "Kit Tudo".
2. Verificar se o título do produto está correto com espaço.
3. Verificar se há metafields customizados (ex.: `custom.display_name`)
   que estejam sobrescrevendo o título sem espaço.
4. No código do tema (arquivo `product-card.liquid` ou similar),
   verificar se há algum filtro Liquid removendo espaços:
   ex.: `{{ product.title | remove: ' ' }}` — se houver, remover.
5. Após correção, limpar o cache do tema e verificar nas seções
   de carrossel da homepage.

**Responsável sugerido:** Desenvolvedor Shopify  
**Tempo estimado:** 30 minutos a 1 hora  

**Critério de sucesso:**  
Os nomes "Kit Duplinha" e "Kit Tudo" aparecem corretamente
com espaço em todos os carrosséis e listagens de produtos.

---

### AÇÃO 06 — Melhorar proposta de valor na newsletter do footer

**Categoria:** UX / Conversão  
**Prioridade:** 🟡 Média  
**Esforço:** Baixo  
**Impacto:** Médio  

**Problema identificado:**  
O formulário de newsletter no footer tem apenas o título
"Receba todas as nossas novidades!" sem oferecer nenhum
incentivo real para o cadastro. Taxas de inscrição em newsletter
sem incentivo são geralmente abaixo de 1%. Com um benefício claro,
podem chegar a 3-5%.

**Objetivo:**  
Aumentar a taxa de inscrição na newsletter criando uma proposta
de valor clara e atraente para o usuário.

**O que fazer:**  
1. Definir internamente qual benefício será oferecido ao inscrito:
   - Opção A: "Ganhe 10% de desconto na primeira compra"
   - Opção B: "Acesse promoções exclusivas antes de todo mundo"
   - Opção C: "Receba dicas de skincare + ofertas semanais"
2. Atualizar o título e subtítulo da seção no Shopify Admin
   > Personalizar > Footer > Seção de Newsletter.
3. Se possível, adicionar um campo de nome além do e-mail
   para personalizar os envios futuros.
4. Garantir que o e-mail de confirmação de inscrição
   já entregue o cupom prometido (configurar via Klaviyo, Mailchimp
   ou o app de e-mail marketing utilizado).
5. Adicionar um microtexto de LGPD abaixo do botão:
   "Ao se inscrever, você concorda com nossa Política de Privacidade.
   Cancele quando quiser."

**Responsável sugerido:** Marketing + Gestor de E-commerce  
**Tempo estimado:** 2 a 3 horas  

**Critério de sucesso:**  
Taxa de inscrição na newsletter aumenta em pelo menos 50%
nos 30 dias após a implementação (medir via Klaviyo ou plataforma
de e-mail marketing utilizada).

---

# 📅 MÉDIO PRAZO — 1 a 3 meses

> Ações que envolvem desenvolvimento ou planejamento mais elaborado.
> Requerem desenvolvedor Shopify pleno ou agência especializada.

---

### AÇÃO 07 — Reformular o layout da página de produto (duas colunas)

**Categoria:** UX / CRO (Otimização de Conversão)  
**Prioridade:** 🔴 Crítica  
**Esforço:** Médio  
**Impacto:** Alto  

**Problema identificado:**  
A página de produto usa layout em coluna única: galeria de imagens
ocupa a largura total no topo (~917px), e as informações de compra
(título, preço, botão de CTA) ficam empilhadas abaixo.
O usuário precisa rolar a página para ver o preço e o botão
"Adicionar ao carrinho" — especialmente crítico em desktop,
onde a expectativa é que essas informações estejam visíveis
lado a lado sem rolagem.
O padrão de mercado em e-commerces de alta conversão
é: imagens à esquerda, informações à direita.

**Objetivo:**  
Exibir simultaneamente a galeria de imagens e as informações
de compra (preço, CTA, volume discount) na mesma dobra da página
(above the fold), sem necessidade de rolagem em desktop.

**O que fazer:**  
1. Solicitar ao desenvolvedor Shopify a criação/modificação
   do template de produto (`product.liquid` ou `main-product.liquid`).
2. Implementar o layout CSS Grid ou Flexbox:
```css
   .product {
     display: grid;
     grid-template-columns: 1fr 1fr;
     gap: 40px;
     align-items: start;
   }
```
3. Coluna esquerda: galeria de imagens com thumbnails abaixo.
4. Coluna direita: título, avaliações, preço, volume discount,
   urgência de estoque, botão "Adicionar ao carrinho",
   botão "Comprar agora" e selos de segurança.
5. Em mobile (< 768px), manter layout empilhado
   (galeria → informações), que já funciona bem.
6. Garantir que a galeria de imagens tenha zoom ao hover (desktop)
   e swipe (mobile).
7. Testar em 5 dispositivos/resoluções diferentes antes de publicar.

**Responsável sugerido:** Desenvolvedor Shopify Pleno  
**Tempo estimado:** 8 a 16 horas  

**Critério de sucesso:**  
Em resolução 1280px (desktop padrão), o título, preço e botão
"Adicionar ao carrinho" estão visíveis sem rolar a página.
Taxa de adição ao carrinho (Add-to-Cart Rate) aumenta em
pelo menos 10% nos 30 dias pós-implementação.

---

### AÇÃO 08 — Implementar botão "Comprar agora" sticky na página de produto

**Categoria:** UX / CRO  
**Prioridade:** 🔴 Alta  
**Esforço:** Médio  
**Impacto:** Alto  

**Problema identificado:**  
A página de produto possui muito conteúdo abaixo do CTA principal
(depoimentos em vídeo, seção de antes/depois, ingredientes,
FAQ de produto). Quando o usuário rola para explorar esse conteúdo,
o botão "Adicionar ao carrinho" some do campo visual.