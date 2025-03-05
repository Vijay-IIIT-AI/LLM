from sentence_transformers import SentenceTransformer, CrossEncoder, util
import pandas as pd
import faiss
import numpy as np
from sklearn.preprocessing import MinMaxScaler  # For score normalization

# Load models
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # For retrieval
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")  # cross-encoder/ms-marco-MiniLM-L-12-v2

# Sample DataFrame with slide content
df = pd.DataFrame({
    'slide_number': [1, 2, 3, 4, 5],
    'page_content': [
        """The Eiffel Tower is a famous landmark in Paris, France. It was designed by Gustave Eiffel 
        and completed in 1889 as part of the World's Fair. The structure stands at 330 meters tall 
        and is one of the most visited monuments in the world, attracting millions of tourists 
        every year. Originally criticized by leading artists and intellectuals of France, 
        the Eiffel Tower has become a cultural icon. The tower has three observation decks 
        offering panoramic views of Paris. Over the years, it has been repainted every seven years 
        to maintain its distinctive look. Its iron structure was a revolutionary engineering 
        achievement in the 19th century.""",

        """루브르 박물관은 세계에서 가장 큰 미술관 중 하나이며, 프랑스 파리에 위치하고 있습니다. 이 박물관은 
        12세기에 요새로 처음 건설되었으며, 이후 루이 14세 시대에 미술관으로 개조되었습니다. 1793년 프랑스 혁명 
        이후 공식적으로 대중에게 개방되었습니다. 가장 유명한 전시 작품 중 하나는 레오나르도 다 빈치의 
        '모나리자'이며, 매년 수백만 명의 관광객들이 이를 보기 위해 방문합니다. 루브르 박물관은 회화, 조각, 
        고대 유물 등 35,000점 이상의 예술품을 소장하고 있으며, 전시 공간만 해도 72,735제곱미터에 이릅니다. 
        박물관 내부에는 이집트, 그리스, 로마의 유물들이 전시되어 있으며, 나폴레옹 1세가 수집한 수많은 작품들도 
        포함되어 있습니다. 1989년 유리 피라미드 입구가 추가되었으며, 현재 루브르 박물관의 상징적인 구조물 
        중 하나가 되었습니다.""", 

        """The Han River (한강) runs through the heart of Seoul, South Korea, stretching over 514 kilometers. 
        It plays a crucial role in Korean history, as many ancient kingdoms, including Baekje, 
        settled along its banks. Today, the Han River is a major recreational and cultural hub. 
        The river is lined with public parks, cycling paths, and outdoor fitness areas. The Seoul 
        Metropolitan Government has invested heavily in revitalizing the riverfront, creating spaces 
        such as Banpo Hangang Park, where people gather for picnics, live music, and the famous 
        Rainbow Fountain show. The river also serves as a natural border between different districts 
        of Seoul, with multiple bridges connecting the northern and southern parts of the city. 
        It has been featured in many Korean dramas and films as a romantic and scenic location. 
        Various water sports such as kayaking and paddleboarding are popular among both locals 
        and tourists. Due to its historical significance and modern appeal, the Han River remains 
        an iconic feature of Seoul.""",

        """경복궁은 조선 왕조(1392-1897)의 첫 번째 궁전으로, 한국 서울의 중심부에 위치하고 있습니다. 
        1395년에 건립된 이 궁전은 조선 왕조의 공식 궁전으로 사용되었습니다. 경복궁은 임진왜란(1592-1598) 
        동안 심각한 피해를 입었지만, 이후 여러 차례 복원되었습니다. 현재 경복궁은 역사적 가치가 높은 문화재로서 
        보호되고 있으며, 주요 관광 명소 중 하나로 자리 잡았습니다. 궁전 내부에는 근정전, 경회루, 자경전 등 
        다양한 건축물이 있으며, 전통 한국식 정원도 포함되어 있습니다. 매년 수많은 관광객들이 경복궁을 방문하며, 
        특히 한복을 입고 방문하면 입장료가 면제되는 이벤트가 인기를 끌고 있습니다. 또한 경복궁에서는 조선 왕실의 
        전통 의식을 재현하는 특별 행사도 정기적으로 개최됩니다. 경복궁은 단순한 궁전이 아니라, 한국 전통 건축의 
        정수를 보여주는 곳이며, 조선 시대의 정치, 문화, 예술의 중심지였습니다.""",  

        """The Statue of Liberty, located in New York Harbor, was a gift from France to the United States 
        in 1886. Designed by Frédéric Auguste Bartholdi, the statue symbolizes freedom and democracy. 
        The structure was constructed in France before being dismantled and shipped to the United States, 
        where it was reassembled on Liberty Island. The statue itself stands 93 meters tall, including 
        its pedestal, and is made of copper, which has developed a green patina over time due to oxidation. 
        Inside the statue, visitors can climb a spiral staircase to reach the crown, where small windows 
        provide panoramic views of New York City. The pedestal houses a museum showcasing the statue's 
        history and its significance in American culture. Over the years, the Statue of Liberty has become 
        a global symbol of hope and opportunity, welcoming immigrants arriving in the United States 
        through Ellis Island. It remains one of the most visited landmarks in the world, attracting 
        millions of tourists annually.""",
    ]
})


# User Query
query = "What is special about the Eiffel Tower?"


# Step 1: Compute Embeddings & Store in FAISS
chunk_embeddings = embedder.encode(df["page_content"].tolist(), convert_to_numpy=True)
dimension = chunk_embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)  # L2 (Euclidean) distance index
index.add(chunk_embeddings)  # Store embeddings in FAISS

# Step 2: Query Embedding & Retrieve Top N Candidates (Increase to 10)
query_embedding = embedder.encode(query, convert_to_numpy=True)
D, I = index.search(np.array([query_embedding]), k=10)  # Retrieve top 10 matches

# Extract top matching slides
df_top_candidates = df.iloc[I[0]].copy()

# Step 3: Rerank using CrossEncoder
query_pairs = [[query, chunk] for chunk in df_top_candidates['page_content']]
df_top_candidates['rerank_score'] = reranker.predict(query_pairs)

# Step 4: Normalize Scores (0-1 for better comparison)
scaler = MinMaxScaler()
df_top_candidates['rerank_score'] = scaler.fit_transform(df_top_candidates[['rerank_score']])

# Step 5: Select Final Top N (e.g., Top 3) and Sort
df_final = df_top_candidates.nlargest(3, 'rerank_score')

# Display final ranked slides with slide numbers
print(df_final[['slide_number', 'page_content', 'rerank_score']])
