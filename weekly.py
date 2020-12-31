from pyecharts import options as opts
from pyecharts.charts import Bar,Pie,Line,Page

if __name__=='__main__':
    page = Page(layout=Page.SimplePageLayout)
    pie = Pie().add('',[['联通混合云管理平台3期',30],['智能城域网虚拟化资源池服务编排系统',70]]).set_global_opts(title_opts=opts.TitleOpts(title="项目占比",subtitle='纯属虚构'))
    pie2 = Pie().add('',[['开发',50],['测试',20],['文档',30]]).set_global_opts(title_opts=opts.TitleOpts(title="联通混合云管理平台3期模块占比",subtitle='纯属虚构'))
    bar = (Bar().add_xaxis(["联通混合云管理平台3期", "智能城域网虚拟化资源池服务编排系统"]).set_global_opts(title_opts=opts.TitleOpts(title='员工项目工时',subtitle='纯属虚构'))
        .add_yaxis("员工1", [5, 20],stack='stack1')
        .add_yaxis("员工2",[6,60],stack='stack1'))

    week_name_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    person1 = [11, 11, 15, 13, 12, 13, 10]
    person2 = [1, 4, 2, 5, 3, 2, 0]

    line = (Line().add_xaxis(week_name_list)
            .add_yaxis('员工1',person1)
            .add_yaxis('员工2',person2)
            .set_global_opts(opts.TitleOpts(title="员工一周工时", subtitle="纯属虚构"), tooltip_opts=opts.TooltipOpts(trigger="axis"))
            )

    page.add(pie)
    page.add(pie2)
    page.add(bar)
    page.add(line)
    page.render('weekly.html')