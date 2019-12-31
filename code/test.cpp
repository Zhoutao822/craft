#include <stdio.h>

#include <stdlib.h>

//表结点

typedef struct ArcNode
{

  int adjvex; //边指向的顶点的位置

  struct ArcNode *nextarc; //指向下一条边的指针

} ArcNode;

//头结点

typedef struct Vnode

{

  int data; //顶点信息

  ArcNode *firstarc; //指向第一条依附该节点边的指针

} Vnode;

bool visit[20];

//图结构

typedef struct Graph

{

  int point; //图的顶点数

  int link; //图的边数

  Vnode *VeArray; //头结点数组指针

  int flag; //图的种类标志位，0为无向图，1为有向图

} AlGraph;

//栈结构

typedef struct
{

  int *elem;

  int Size;

  int top;

} Stack;

//初始化图

void InitGraph(AlGraph *p, int ve, int arc)

{

  p->point = ve;

  p->link = arc;

  p->flag = 0;

  p->VeArray = (Vnode *)malloc(sizeof(Vnode) * ve);
}

//用邻接表存储图

void CreateGraph(AlGraph *p)

{

  int i, j;

  int index;

  ArcNode *Q, *S;

  printf("请依次输入各顶点\n");

  for (i = 0; i < p->point; i++)

  {

    scanf("%d", &index);

    p->VeArray[i].data = index;

    p->VeArray[i].firstarc = NULL;

  } //存储顶点头指针

  for (i = 0; i < p->point; i++)

  { //为每个顶点建立邻接表

    S = (ArcNode *)malloc(sizeof(ArcNode));

    printf("依次输入与顶点 %d相邻的顶点并以0结束：", p->VeArray[i].data);

    scanf("%d", &index);

    if (index)

    {

      j = 0;

      while (index != p->VeArray[j].data)

        j++;

      S->adjvex = j;

      p->VeArray[i].firstarc = S;

      Q = S;
    }

    else

      continue;

    scanf("%d", &index);

    while (index)

    {

      S = (ArcNode *)malloc(sizeof(ArcNode));

      j = 0;

      while (index != p->VeArray[j].data)

        j++;

      S->adjvex = j;

      Q->nextarc = S;

      Q = S;

      scanf("%d", &index);
    }

    Q->nextarc = NULL;
  }
}

//输出邻接表

void showGraph(AlGraph *p)

{

  int i;

  ArcNode *temp;

  printf("顶点位置\t顶点名称\t邻接顶点的位置\n");

  for (i = 0; i < p->point; i++)

  {

    printf("%4d\t\t%d ->\t\t", i, p->VeArray[i].data);

    temp = p->VeArray[i].firstarc;

    while (temp)

    {

      printf("%d->", temp->adjvex);

      temp = temp->nextarc;
    }

    printf("\n");
  }
}

//非递归深度优先搜索无向图

void DFS(AlGraph p, Vnode v)

{

  //初始化访问数组

  int i, k;

  ArcNode *G;

  for (i = 1; i <= p.point; i++)

    visit[i] = false;

  Stack sta;

  //初始化栈

  sta.elem = (int *)malloc(sizeof(int) * p.point);

  sta.Size = p.point;

  sta.top = 0;

  //胜利进栈

  sta.elem[sta.top] = v.data;

  sta.top++;

  visit[v.data] = true;

  while (sta.top) //栈不为空

  {

    //出栈，访问元素

    k = sta.elem[sta.top - 1];

    printf("%4d->", k);

    sta.top--;

    //将与k相邻且未入过栈的顶点入栈

    i = 0;

    while (p.VeArray[i].data != k)

      i++;

    G = p.VeArray[i].firstarc;

    while (G)

    {

      if (!visit[p.VeArray[G->adjvex].data])

      {

        //元素入栈

        sta.elem[sta.top] = p.VeArray[G->adjvex].data;

        sta.top++;

        visit[p.VeArray[G->adjvex].data] = true;
      }

      else

        G = G->nextarc;
    }
  }

  printf("\n");
}

int main()

{

  int ve, arc;

  AlGraph p;

  printf("请输入无向图的顶点数和边数：\n");

  scanf("%d%d", &ve, &arc);

  InitGraph(&p, ve, arc);

  CreateGraph(&p);

  printf("\n无向图的邻接表存储结构如下：\n");

  showGraph(&p);

  printf("深度优先搜索无向图序列如下:\n");

  DFS(p, p.VeArray[0]);
}
