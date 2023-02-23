import React, { ReactNode, useMemo } from 'react'
import styled from 'styled-components'
import { VariantsPlot } from 'src/components/Variants/VariantsPlot'
import { VariantsSidebar } from 'src/components/Variants/VariantsSidebar'
import { PageContainerHorizontal } from 'src/components/Layout/PageContainer'
import { useTranslationSafe } from 'src/helpers/useTranslationSafe'
import { usePathogen, useVariantDataQuery, useVariantsDataQuery } from 'src/io/getData'
import { Col, Row } from 'reactstrap'
import urljoin from 'url-join'
import { Link } from 'src/components/Link/Link'

export interface VariantsPageProps {
  pathogenName: string
  variantName: string
}

export function VariantPage({ pathogenName, variantName }: VariantsPageProps) {
  const { t } = useTranslationSafe()
  const pathogen = usePathogen(pathogenName)
  const {
    variantData: { variant },
  } = useVariantDataQuery(pathogenName, variantName)
  const { variants } = useVariantsDataQuery(pathogenName)

  const { prev, next } = useMemo(() => {
    const i = variants.indexOf(variant)
    let prev: ReactNode = null
    if (i > 0) {
      const prevName = variants[i - 1]
      prev = (
        <Link href={urljoin('pathogen', pathogenName, 'variants', prevName)}>
          {t('Previous: {{name}}', { name: prevName })}
        </Link>
      )
    }
    let next: ReactNode = null
    if (i < variants.length - 1) {
      const nextName = variants[i + 1]
      next = (
        <Link href={urljoin('pathogen', pathogenName, 'variants', nextName)}>
          {t('Next: {{name}}', { name: nextName })}
        </Link>
      )
    }
    return { prev, next }
  }, [pathogenName, t, variant, variants])

  return (
    <PageContainerHorizontal>
      <VariantsSidebar pathogenName={pathogenName} />

      <MainContent>
        <MainContentInner>
          <Row noGutters>
            <Col>
              <span className="d-flex w-100">
                <span className="mr-auto">{prev}</span>
                <span className="ml-auto">{next}</span>
              </span>
              <h4 className="text-center">
                {t('{{name}}, variant {{variant}}', {
                  name: t(pathogen.nameFriendly),
                  variant: variantName,
                })}
              </h4>
            </Col>
          </Row>

          <VariantsPlot pathogen={pathogen} variantName={variant} />
        </MainContentInner>
      </MainContent>
    </PageContainerHorizontal>
  )
}

const MainContent = styled.div`
  display: flex;
  flex-direction: row;
  flex: 1 1 100%;
  overflow: hidden;
`

const MainContentInner = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1 1 100%;
  overflow: hidden;
`